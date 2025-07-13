"""
FastAPI routes for schematic file management and validation.

Provides endpoints for:
- Uploading schematic files (GDSII, DXF, SVG)
- Retrieving schematic data and metadata
- Validating strategies against schematics
- Exporting schematics in different formats
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query, Path
from fastapi.responses import Response
from pydantic import BaseModel, Field
import logging

from ...services.schematic_service import get_schematic_service
from ...services.strategy_service import get_strategy_service
from ...core.models.schematic import SchematicFormat, ValidationStatus
from ...core.models.errors import StandardErrorResponse, create_validation_error, create_not_found_error

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schematics", tags=["schematics"])


# Request/Response Models
class SchematicUploadRequest(BaseModel):
    """Request model for schematic upload."""
    created_by: str = Field(..., description="User who is uploading the schematic")
    coordinate_scale: Optional[float] = Field(1.0, description="Scale factor for coordinates")
    die_size_filter: Optional[List[float]] = Field(None, description="Min/max die size filter [min, max]")
    target_cell: Optional[str] = Field(None, description="Specific cell to parse (GDSII only)")
    target_layer: Optional[str] = Field(None, description="Specific layer to process")


class SchematicResponse(BaseModel):
    """Response model for schematic data."""
    id: str
    filename: str
    format_type: str
    upload_date: str
    die_count: int
    available_die_count: int
    coordinate_system: str
    wafer_size: Optional[str]
    statistics: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]


class SchematicListResponse(BaseModel):
    """Response model for schematic list."""
    schematics: List[Dict[str, Any]]
    total_count: int


class ValidationRequest(BaseModel):
    """Request model for strategy validation."""
    strategy_id: str = Field(..., description="ID of strategy to validate")
    validated_by: str = Field(..., description="User performing validation")


class ValidationResponse(BaseModel):
    """Response model for validation results."""
    validation_id: str
    schematic_id: str
    strategy_id: str
    validation_status: str
    alignment_score: float
    coverage_percentage: float
    total_points: int
    valid_points: int
    error_count: int
    warning_count: int
    recommendations: List[str]
    validation_date: str


@router.post("/upload", response_model=SchematicResponse)
async def upload_schematic(
    file: UploadFile = File(..., description="Schematic file to upload"),
    created_by: str = Query(..., description="User uploading the file"),
    coordinate_scale: float = Query(1.0, description="Scale factor for coordinates"),
    die_size_filter_min: Optional[float] = Query(None, description="Minimum die size"),
    die_size_filter_max: Optional[float] = Query(None, description="Maximum die size"),
    target_cell: Optional[str] = Query(None, description="Specific cell to parse (GDSII)"),
    target_layer: Optional[str] = Query(None, description="Specific layer to process")
):
    """
    Upload and parse a schematic file.
    
    Supports GDSII (.gds, .gdsii), DXF (.dxf), and SVG (.svg) formats.
    Returns parsed schematic data with die boundaries and metadata.
    """
    logger.info(f"Processing schematic upload: {file.filename}")
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file size (limit to 100MB)
    if file.size and file.size > 100 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 100MB)")
    
    try:
        # Prepare parsing options
        parse_options = {
            'coordinate_scale': coordinate_scale,
            'target_cell': target_cell,
            'target_layer': target_layer
        }
        
        if die_size_filter_min is not None and die_size_filter_max is not None:
            parse_options['die_size_filter'] = (die_size_filter_min, die_size_filter_max)
        
        # Upload and parse
        schematic_service = get_schematic_service()
        schematic_data = schematic_service.upload_schematic(
            file_content=file.file,
            filename=file.filename,
            created_by=created_by,
            **parse_options
        )
        
        # Return response
        return SchematicResponse(
            id=schematic_data.id,
            filename=schematic_data.filename,
            format_type=schematic_data.format_type.value,
            upload_date=schematic_data.upload_date.isoformat(),
            die_count=schematic_data.die_count,
            available_die_count=schematic_data.available_die_count,
            coordinate_system=schematic_data.coordinate_system.value,
            wafer_size=schematic_data.wafer_size,
            statistics=schematic_data.get_statistics(),
            metadata=schematic_data.to_dict().get('metadata')
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading schematic: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during upload")


@router.get("/", response_model=SchematicListResponse)
async def list_schematics(
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    format_type: Optional[str] = Query(None, description="Filter by format (gdsii, dxf, svg)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results")
):
    """
    List available schematics with filtering options.
    
    Returns metadata for all accessible schematics with optional filtering
    by creator and format type.
    """
    try:
        schematic_service = get_schematic_service()
        
        # Convert format string to enum if provided
        format_enum = None
        if format_type:
            try:
                format_enum = SchematicFormat(format_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid format type: {format_type}")
        
        schematics = schematic_service.list_schematics(
            created_by=created_by,
            format_type=format_enum,
            limit=limit
        )
        
        return SchematicListResponse(
            schematics=schematics,
            total_count=len(schematics)
        )
        
    except Exception as e:
        logger.error(f"Error listing schematics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{schematic_id}", response_model=SchematicResponse)
async def get_schematic(
    schematic_id: str = Path(..., description="Schematic ID")
):
    """
    Get detailed schematic data by ID.
    
    Returns complete schematic information including die boundaries,
    metadata, and layout statistics.
    """
    try:
        schematic_service = get_schematic_service()
        schematic_data = schematic_service.get_schematic(schematic_id)
        
        if not schematic_data:
            raise HTTPException(status_code=404, detail=f"Schematic not found: {schematic_id}")
        
        return SchematicResponse(
            id=schematic_data.id,
            filename=schematic_data.filename,
            format_type=schematic_data.format_type.value,
            upload_date=schematic_data.upload_date.isoformat(),
            die_count=schematic_data.die_count,
            available_die_count=schematic_data.available_die_count,
            coordinate_system=schematic_data.coordinate_system.value,
            wafer_size=schematic_data.wafer_size,
            statistics=schematic_data.get_statistics(),
            metadata=schematic_data.to_dict().get('metadata')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting schematic {schematic_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{schematic_id}/die-boundaries")
async def get_die_boundaries(
    schematic_id: str = Path(..., description="Schematic ID"),
    limit: Optional[int] = Query(None, description="Limit number of boundaries returned")
):
    """
    Get die boundary data for a schematic.
    
    Returns detailed die boundary information including coordinates,
    availability status, and metadata for each die.
    """
    try:
        schematic_service = get_schematic_service()
        schematic_data = schematic_service.get_schematic(schematic_id)
        
        if not schematic_data:
            raise HTTPException(status_code=404, detail=f"Schematic not found: {schematic_id}")
        
        boundaries = schematic_data.die_boundaries
        if limit:
            boundaries = boundaries[:limit]
        
        return {
            "schematic_id": schematic_id,
            "total_die_count": len(schematic_data.die_boundaries),
            "returned_count": len(boundaries),
            "die_boundaries": [
                {
                    "die_id": die.die_id,
                    "x_min": die.x_min,
                    "y_min": die.y_min,
                    "x_max": die.x_max,
                    "y_max": die.y_max,
                    "center_x": die.center_x,
                    "center_y": die.center_y,
                    "width": die.width,
                    "height": die.height,
                    "area": die.area,
                    "available": die.available,
                    "metadata": die.metadata
                }
                for die in boundaries
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting die boundaries for {schematic_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{schematic_id}/validate", response_model=ValidationResponse)
async def validate_strategy(
    schematic_id: str = Path(..., description="Schematic ID"),
    request: ValidationRequest = None
):
    """
    Validate a strategy against schematic data.
    
    Checks if strategy sampling points align with die boundaries,
    calculates coverage statistics, and identifies conflicts.
    """
    try:
        schematic_service = get_schematic_service()
        strategy_service = get_strategy_service()
        
        # Get schematic
        schematic_data = schematic_service.get_schematic(schematic_id)
        if not schematic_data:
            raise HTTPException(status_code=404, detail=f"Schematic not found: {schematic_id}")
        
        # Get strategy
        strategy = strategy_service.get_strategy(request.strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail=f"Strategy not found: {request.strategy_id}")
        
        # Perform validation
        validation_result = schematic_service.validate_strategy_against_schematic(
            strategy=strategy,
            schematic_id=schematic_id,
            validated_by=request.validated_by
        )
        
        return ValidationResponse(
            validation_id=validation_result.validation_id,
            schematic_id=validation_result.schematic_id,
            strategy_id=validation_result.strategy_id,
            validation_status=validation_result.validation_status.value,
            alignment_score=validation_result.alignment_score,
            coverage_percentage=validation_result.coverage_percentage,
            total_points=validation_result.total_strategy_points,
            valid_points=validation_result.valid_strategy_points,
            error_count=len([c for c in validation_result.conflicts if c.severity == "error"]),
            warning_count=len(validation_result.warnings) + len([c for c in validation_result.conflicts if c.severity == "warning"]),
            recommendations=validation_result.recommendations,
            validation_date=validation_result.validation_date.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating strategy against schematic: {e}")
        raise HTTPException(status_code=500, detail="Validation failed due to internal error")


@router.get("/{schematic_id}/validations")
async def list_validations(
    schematic_id: str = Path(..., description="Schematic ID"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results")
):
    """
    List validation results for a schematic.
    
    Returns summary information for all validations performed
    against this schematic.
    """
    try:
        schematic_service = get_schematic_service()
        
        # Verify schematic exists
        schematic_data = schematic_service.get_schematic(schematic_id)
        if not schematic_data:
            raise HTTPException(status_code=404, detail=f"Schematic not found: {schematic_id}")
        
        # Get validation results
        validations = schematic_service.list_validation_results(
            schematic_id=schematic_id,
            limit=limit
        )
        
        return {
            "schematic_id": schematic_id,
            "total_validations": len(validations),
            "validations": validations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing validations for schematic {schematic_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/validations/{validation_id}")
async def get_validation_result(
    validation_id: str = Path(..., description="Validation ID")
):
    """
    Get detailed validation result by ID.
    
    Returns complete validation information including conflicts,
    warnings, and detailed recommendations.
    """
    try:
        schematic_service = get_schematic_service()
        validation_result = schematic_service.get_validation_result(validation_id)
        
        if not validation_result:
            raise HTTPException(status_code=404, detail=f"Validation result not found: {validation_id}")
        
        return validation_result.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting validation result {validation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{schematic_id}/export/{format_type}")
async def export_schematic(
    schematic_id: str = Path(..., description="Schematic ID"),
    format_type: str = Path(..., description="Export format (svg, dxf)")
):
    """
    Export schematic data in specified format.
    
    Converts schematic data to the requested format and returns
    the binary file data with appropriate content type.
    """
    try:
        # Validate format
        valid_formats = ["svg", "dxf"]
        if format_type not in valid_formats:
            raise HTTPException(status_code=400, detail=f"Unsupported export format: {format_type}")
        
        schematic_service = get_schematic_service()
        
        # Verify schematic exists
        schematic_data = schematic_service.get_schematic(schematic_id)
        if not schematic_data:
            raise HTTPException(status_code=404, detail=f"Schematic not found: {schematic_id}")
        
        # Export to format
        format_enum = SchematicFormat(format_type)
        export_data = schematic_service.export_schematic(schematic_id, format_enum)
        
        # Determine content type and filename
        content_types = {
            "svg": "image/svg+xml",
            "dxf": "application/dxf"
        }
        
        filename = f"{schematic_data.filename.rsplit('.', 1)[0]}.{format_type}"
        
        return Response(
            content=export_data,
            media_type=content_types[format_type],
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting schematic {schematic_id} as {format_type}: {e}")
        raise HTTPException(status_code=500, detail="Export failed due to internal error")


@router.delete("/{schematic_id}")
async def delete_schematic(
    schematic_id: str = Path(..., description="Schematic ID")
):
    """
    Delete a schematic and all associated validation results.
    
    Permanently removes the schematic data and any validation
    results that reference it.
    """
    try:
        schematic_service = get_schematic_service()
        
        # Verify schematic exists
        schematic_data = schematic_service.get_schematic(schematic_id)
        if not schematic_data:
            raise HTTPException(status_code=404, detail=f"Schematic not found: {schematic_id}")
        
        # Delete schematic
        success = schematic_service.delete_schematic(schematic_id)
        
        if success:
            return {"message": f"Schematic {schematic_id} deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete schematic")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting schematic {schematic_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/formats/supported")
async def get_supported_formats():
    """
    Get list of supported schematic file formats.
    
    Returns information about supported formats including
    file extensions and parser capabilities.
    """
    return {
        "supported_formats": [
            {
                "format": "gdsii",
                "description": "GDSII Stream Format for IC layouts",
                "extensions": [".gds", ".gdsii"],
                "features": ["die_boundaries", "text_labels", "cell_references"],
                "parser_status": "available"
            },
            {
                "format": "dxf",
                "description": "AutoCAD Drawing Exchange Format",
                "extensions": [".dxf"],
                "features": ["geometric_entities", "text_elements", "block_inserts"],
                "parser_status": "available"
            },
            {
                "format": "svg",
                "description": "Scalable Vector Graphics",
                "extensions": [".svg"],
                "features": ["shape_elements", "text_labels", "grouped_elements"],
                "parser_status": "available"
            }
        ],
        "upload_limits": {
            "max_file_size": "100MB",
            "supported_coordinate_systems": ["cartesian", "gdsii_units", "cad_units"],
            "die_detection_methods": ["shape_analysis", "text_parsing", "reference_extraction"]
        }
    }