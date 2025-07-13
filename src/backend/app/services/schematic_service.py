"""
Schematic service layer for managing schematic data import, validation, and export.

This service provides business logic for:
- Parsing schematic files (GDSII, DXF, SVG)
- Validating strategies against schematic data
- Converting between different schematic formats
- Managing schematic persistence
"""
import logging
from typing import List, Dict, Any, Optional, BinaryIO
from pathlib import Path
import tempfile
import uuid

from ..core.models.schematic import (
    SchematicData, SchematicValidationResult, SchematicFormat, 
    ValidationStatus, ValidationConflict, ValidationWarning
)
from ..core.parsers import GDSIIParser, DXFParser, SVGParser
from ..core.strategy.definition import StrategyDefinition
from ..core.database.models import SchematicModel, SchematicValidationModel, db_manager

logger = logging.getLogger(__name__)


class SchematicService:
    """Service for managing schematic data operations."""
    
    def __init__(self):
        self.parsers = {
            SchematicFormat.GDSII: GDSIIParser(),
            SchematicFormat.DXF: DXFParser(),
            SchematicFormat.SVG: SVGParser()
        }
        
        # Initialize database tables
        try:
            db_manager.create_tables()
        except Exception as e:
            logger.warning(f"Could not initialize database tables: {e}")
    
    def upload_schematic(self, file_content: BinaryIO, filename: str, 
                        created_by: str, **kwargs) -> SchematicData:
        """
        Upload and parse a schematic file.
        
        Args:
            file_content: Binary file content
            filename: Original filename
            created_by: User who uploaded the file
            **kwargs: Additional parsing options
        
        Returns:
            SchematicData object with parsed information
        """
        logger.info(f"Processing schematic upload: {filename}")
        
        # Detect format from filename
        file_format = self._detect_format(filename)
        if file_format == SchematicFormat.UNKNOWN:
            raise ValueError(f"Unsupported file format: {Path(filename).suffix}")
        
        # Get appropriate parser
        parser = self.parsers.get(file_format)
        if not parser:
            raise ValueError(f"No parser available for format: {file_format}")
        
        # Save to temporary file for parsing
        with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as temp_file:
            temp_file.write(file_content.read())
            temp_path = temp_file.name
        
        try:
            # Parse the file
            schematic_data = parser.parse_file(temp_path, **kwargs)
            
            # Update filename to original
            schematic_data.filename = filename
            
            # Save to database
            self._save_schematic(schematic_data, created_by)
            
            logger.info(f"Successfully processed schematic {filename}: {len(schematic_data.die_boundaries)} dies")
            
            return schematic_data
            
        finally:
            # Clean up temporary file
            try:
                Path(temp_path).unlink()
            except:
                pass
    
    def get_schematic(self, schematic_id: str) -> Optional[SchematicData]:
        """Get schematic data by ID."""
        try:
            session = db_manager.get_session()
            schematic_model = session.query(SchematicModel).filter(
                SchematicModel.id == schematic_id
            ).first()
            
            if schematic_model:
                return schematic_model.to_schematic_data()
            
        except Exception as e:
            logger.error(f"Error retrieving schematic {schematic_id}: {e}")
        
        return None
    
    def list_schematics(self, created_by: Optional[str] = None, 
                       format_type: Optional[SchematicFormat] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """List available schematics with metadata."""
        try:
            session = db_manager.get_session()
            query = session.query(SchematicModel)
            
            if created_by:
                query = query.filter(SchematicModel.created_by == created_by)
            
            if format_type:
                query = query.filter(SchematicModel.format_type == format_type.value)
            
            schematics = query.order_by(SchematicModel.upload_date.desc()).limit(limit).all()
            
            return [
                {
                    'id': s.id,
                    'filename': s.filename,
                    'format_type': s.format_type,
                    'upload_date': s.upload_date.isoformat(),
                    'die_count': s.die_count,
                    'available_die_count': s.available_die_count,
                    'wafer_size': s.wafer_size,
                    'created_by': s.created_by
                }
                for s in schematics
            ]
            
        except Exception as e:
            logger.error(f"Error listing schematics: {e}")
            return []
    
    def validate_strategy_against_schematic(self, strategy: StrategyDefinition, 
                                          schematic_id: str,
                                          validated_by: str) -> SchematicValidationResult:
        """
        Validate a strategy against schematic data.
        
        Args:
            strategy: Strategy to validate
            schematic_id: ID of schematic to validate against
            validated_by: User performing validation
        
        Returns:
            SchematicValidationResult with validation details
        """
        logger.info(f"Validating strategy {strategy.id} against schematic {schematic_id}")
        
        # Get schematic data
        schematic = self.get_schematic(schematic_id)
        if not schematic:
            raise ValueError(f"Schematic not found: {schematic_id}")
        
        # Create validation result
        validation_result = SchematicValidationResult(
            schematic_id=schematic_id,
            strategy_id=strategy.id,
            validation_status=ValidationStatus.NOT_VALIDATED
        )
        
        try:
            # Compile strategy to get sampling points
            from ..core.strategy.compilation import StrategyCompiler
            compiler = StrategyCompiler()
            
            # Convert schematic to wafer map for strategy execution
            wafer_map = schematic.to_wafer_map()
            compiled_strategy = compiler.compile_strategy(strategy)
            
            # Execute strategy to get sampling points
            execution_context = compiler.create_execution_context(wafer_map, {})
            sampling_points = compiled_strategy.execute(execution_context)
            
            # Validate each sampling point against schematic
            validation_result.total_strategy_points = len(sampling_points)
            valid_points = 0
            
            for point in sampling_points:
                die_boundary = schematic.get_die_at_coordinates(point.x, point.y)
                
                if die_boundary is None:
                    # Point is outside any die boundary
                    validation_result.add_conflict(
                        conflict_type="out_of_bounds",
                        strategy_point=(point.x, point.y),
                        description=f"Strategy point ({point.x}, {point.y}) is outside all die boundaries",
                        severity="error",
                        recommendation="Adjust strategy rules to stay within die boundaries"
                    )
                elif not die_boundary.available:
                    # Point is on an unavailable die
                    validation_result.add_conflict(
                        conflict_type="unavailable_die",
                        strategy_point=(point.x, point.y),
                        description=f"Strategy point ({point.x}, {point.y}) targets unavailable die {die_boundary.die_id}",
                        severity="warning",
                        recommendation="Consider marking die as available or adjust strategy",
                        affected_die_id=die_boundary.die_id
                    )
                    valid_points += 1  # Count as valid but with warning
                else:
                    # Point is valid
                    valid_points += 1
            
            validation_result.valid_strategy_points = valid_points
            validation_result.coverage_percentage = (valid_points / len(sampling_points) * 100) if sampling_points else 0
            
            # Add general warnings
            if validation_result.coverage_percentage < 90:
                validation_result.add_warning(
                    warning_type="low_coverage",
                    description=f"Strategy coverage is only {validation_result.coverage_percentage:.1f}%",
                    recommendation="Consider adjusting strategy rules to improve coverage"
                )
            
            # Calculate final validation status
            if validation_result.has_errors:
                validation_result.validation_status = ValidationStatus.FAIL
            elif validation_result.has_warnings:
                validation_result.validation_status = ValidationStatus.WARNING
            else:
                validation_result.validation_status = ValidationStatus.PASS
            
            # Calculate alignment score
            validation_result.calculate_alignment_score()
            
            # Generate recommendations
            validation_result.recommendations = self._generate_recommendations(validation_result, schematic)
            
            # Save validation result
            self._save_validation_result(validation_result, validated_by)
            
            logger.info(f"Validation completed: {validation_result.validation_status.value}, score: {validation_result.alignment_score}")
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            validation_result.validation_status = ValidationStatus.FAIL
            validation_result.add_conflict(
                conflict_type="validation_error",
                strategy_point=(0, 0),
                description=f"Validation failed with error: {str(e)}",
                severity="error"
            )
        
        return validation_result
    
    def get_validation_result(self, validation_id: str) -> Optional[SchematicValidationResult]:
        """Get validation result by ID."""
        try:
            session = db_manager.get_session()
            validation_model = session.query(SchematicValidationModel).filter(
                SchematicValidationModel.validation_id == validation_id
            ).first()
            
            if validation_model:
                return validation_model.to_validation_result()
                
        except Exception as e:
            logger.error(f"Error retrieving validation result {validation_id}: {e}")
        
        return None
    
    def list_validation_results(self, schematic_id: Optional[str] = None,
                               strategy_id: Optional[str] = None,
                               limit: int = 50) -> List[Dict[str, Any]]:
        """List validation results with summary information."""
        try:
            session = db_manager.get_session()
            query = session.query(SchematicValidationModel)
            
            if schematic_id:
                query = query.filter(SchematicValidationModel.schematic_id == schematic_id)
            
            if strategy_id:
                query = query.filter(SchematicValidationModel.strategy_id == strategy_id)
            
            validations = query.order_by(SchematicValidationModel.validation_date.desc()).limit(limit).all()
            
            return [
                {
                    'validation_id': v.validation_id,
                    'schematic_id': v.schematic_id,
                    'strategy_id': v.strategy_id,
                    'validation_date': v.validation_date.isoformat(),
                    'validation_status': v.validation_status,
                    'alignment_score': v.alignment_score / 100.0,
                    'coverage_percentage': v.coverage_percentage,
                    'total_points': v.total_strategy_points,
                    'valid_points': v.valid_strategy_points,
                    'validated_by': v.validated_by
                }
                for v in validations
            ]
            
        except Exception as e:
            logger.error(f"Error listing validation results: {e}")
            return []
    
    def export_schematic(self, schematic_id: str, target_format: SchematicFormat) -> bytes:
        """
        Export schematic data to different format.
        
        Args:
            schematic_id: ID of schematic to export
            target_format: Target format for export
        
        Returns:
            Binary data in target format
        """
        schematic = self.get_schematic(schematic_id)
        if not schematic:
            raise ValueError(f"Schematic not found: {schematic_id}")
        
        if target_format == SchematicFormat.SVG:
            return self._export_to_svg(schematic)
        elif target_format == SchematicFormat.DXF:
            return self._export_to_dxf(schematic)
        else:
            raise ValueError(f"Export to {target_format} not supported")
    
    def delete_schematic(self, schematic_id: str) -> bool:
        """Delete a schematic and all associated validation results."""
        try:
            session = db_manager.get_session()
            
            # Delete validation results first
            session.query(SchematicValidationModel).filter(
                SchematicValidationModel.schematic_id == schematic_id
            ).delete()
            
            # Delete schematic
            deleted_count = session.query(SchematicModel).filter(
                SchematicModel.id == schematic_id
            ).delete()
            
            session.commit()
            
            return deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting schematic {schematic_id}: {e}")
            return False
    
    def _detect_format(self, filename: str) -> SchematicFormat:
        """Detect schematic format from filename."""
        suffix = Path(filename).suffix.lower()
        
        format_map = {
            '.gds': SchematicFormat.GDSII,
            '.gdsii': SchematicFormat.GDSII,
            '.dxf': SchematicFormat.DXF,
            '.svg': SchematicFormat.SVG
        }
        
        return format_map.get(suffix, SchematicFormat.UNKNOWN)
    
    def _save_schematic(self, schematic_data: SchematicData, created_by: str):
        """Save schematic data to database."""
        try:
            session = db_manager.get_session()
            schematic_model = SchematicModel.from_schematic_data(schematic_data, created_by)
            session.add(schematic_model)
            session.commit()
        except Exception as e:
            logger.error(f"Error saving schematic to database: {e}")
            # Continue without database persistence
    
    def _save_validation_result(self, validation_result: SchematicValidationResult, validated_by: str):
        """Save validation result to database."""
        try:
            session = db_manager.get_session()
            validation_model = SchematicValidationModel.from_validation_result(validation_result, validated_by)
            session.add(validation_model)
            session.commit()
        except Exception as e:
            logger.error(f"Error saving validation result to database: {e}")
            # Continue without database persistence
    
    def _generate_recommendations(self, validation_result: SchematicValidationResult, 
                                 schematic: SchematicData) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if validation_result.alignment_score < 0.7:
            recommendations.append("Consider adjusting strategy rules to better align with die layout")
        
        if validation_result.coverage_percentage < 80:
            recommendations.append("Increase sampling density to improve wafer coverage")
        
        error_count = len([c for c in validation_result.conflicts if c.severity == "error"])
        if error_count > 0:
            recommendations.append(f"Fix {error_count} critical errors before deploying strategy")
        
        if len(validation_result.warnings) > 5:
            recommendations.append("Review and address validation warnings for optimal performance")
        
        return recommendations
    
    def _export_to_svg(self, schematic: SchematicData) -> bytes:
        """Export schematic data as SVG."""
        # Create simple SVG representation
        bounds = schematic.layout_bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     viewBox="{bounds[0]} {bounds[1]} {width} {height}"
     width="{width}" height="{height}">
  <title>{schematic.filename} - Die Layout</title>
  <desc>Wafer layout with {len(schematic.die_boundaries)} dies</desc>
'''
        
        # Add die rectangles
        for die in schematic.die_boundaries:
            color = "#4CAF50" if die.available else "#F44336"
            svg_content += f'''  <rect x="{die.x_min}" y="{die.y_min}" 
       width="{die.width}" height="{die.height}"
       fill="{color}" stroke="#333" stroke-width="1" opacity="0.7"/>
  <text x="{die.center_x}" y="{die.center_y}" 
        text-anchor="middle" dominant-baseline="central" 
        font-size="8" fill="white">{die.die_id}</text>
'''
        
        svg_content += '</svg>'
        
        return svg_content.encode('utf-8')
    
    def _export_to_dxf(self, schematic: SchematicData) -> bytes:
        """Export schematic data as DXF."""
        try:
            import ezdxf
            
            # Create new DXF document
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Add die rectangles
            for die in schematic.die_boundaries:
                # Create rectangle
                points = [
                    (die.x_min, die.y_min),
                    (die.x_max, die.y_min),
                    (die.x_max, die.y_max),
                    (die.x_min, die.y_max),
                    (die.x_min, die.y_min)  # Close the rectangle
                ]
                
                layer_name = "AVAILABLE_DIES" if die.available else "UNAVAILABLE_DIES"
                
                # Ensure layer exists
                if layer_name not in doc.layers:
                    doc.layers.new(layer_name)
                
                # Add polyline
                msp.add_lwpolyline(points, close=True, dxfattribs={'layer': layer_name})
                
                # Add text label
                msp.add_text(
                    die.die_id,
                    dxfattribs={'layer': 'TEXT', 'height': min(die.width, die.height) * 0.1}
                ).set_pos((die.center_x, die.center_y))
            
            # Save to bytes
            import io
            buffer = io.BytesIO()
            doc.write(buffer)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error exporting to DXF: {e}")
            raise ValueError(f"DXF export failed: {str(e)}")


# Singleton instance
_schematic_service = None

def get_schematic_service() -> SchematicService:
    """Get singleton instance of SchematicService."""
    global _schematic_service
    if _schematic_service is None:
        _schematic_service = SchematicService()
    return _schematic_service