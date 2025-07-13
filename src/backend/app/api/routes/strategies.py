"""
Strategy API Routes - RESTful endpoints for strategy management.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import datetime

from ...core.strategy.definition import StrategyDefinition, StrategyType, StrategyLifecycle
from ...core.strategy.repository import StrategyManager, StrategyRepository
from ...core.strategy.compilation import StrategyCompiler
from ...services.strategy_service import StrategyService
from ...core.models.errors import (
    StandardErrorResponse, ValidationErrorResponse, NotFoundErrorResponse,
    create_validation_error, create_not_found_error, create_business_logic_error
)


router = APIRouter(prefix="/api/v1/strategies", tags=["strategies"])


# Pydantic models for API
class StrategyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    process_step: str = Field(..., min_length=1)
    tool_type: str = Field(..., min_length=1)
    strategy_type: StrategyType = StrategyType.CUSTOM
    author: str = Field(..., min_length=1)


class StrategyUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[List[Dict[str, Any]]] = None
    conditions: Optional[Dict[str, Any]] = None
    transformations: Optional[Dict[str, Any]] = None


class StrategyResponse(BaseModel):
    id: str
    name: str
    description: str
    strategy_type: str
    process_step: str
    tool_type: str
    version: str
    author: str
    created_at: datetime
    modified_at: datetime
    lifecycle_state: str
    rule_count: int
    
    @classmethod
    def from_definition(cls, definition: StrategyDefinition) -> 'StrategyResponse':
        return cls(
            id=definition.id,
            name=definition.name,
            description=definition.description,
            strategy_type=definition.strategy_type.value,
            process_step=definition.process_step,
            tool_type=definition.tool_type,
            version=definition.version,
            author=definition.author,
            created_at=definition.created_at,
            modified_at=definition.modified_at,
            lifecycle_state=definition.lifecycle_state.value,
            rule_count=len(definition.rules)
        )


class SimulationRequest(BaseModel):
    wafer_map_data: Dict[str, Any]
    process_parameters: Dict[str, Any] = Field(default_factory=dict)
    tool_constraints: Dict[str, Any] = Field(default_factory=dict)


class SimulationResult(BaseModel):
    selected_points: List[Dict[str, Any]]
    coverage_stats: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    warnings: List[str] = Field(default_factory=list)


# Dependency injection - singleton for development
_strategy_service = None

def get_strategy_service() -> StrategyService:
    global _strategy_service
    if _strategy_service is None:
        _strategy_service = StrategyService()
    return _strategy_service


@router.post("/", response_model=StrategyResponse, responses={400: {"model": ValidationErrorResponse}})
async def create_strategy(
    request: StrategyCreateRequest,
    service: StrategyService = Depends(get_strategy_service)
):
    """Create a new strategy definition."""
    try:
        definition = service.create_strategy(
            name=request.name,
            description=request.description,
            process_step=request.process_step,
            tool_type=request.tool_type,
            strategy_type=request.strategy_type,
            author=request.author
        )
        return StrategyResponse.from_definition(definition)
    except ValueError as e:
        error_response = create_validation_error(str(e))
        raise HTTPException(status_code=400, detail=error_response.dict())
    except Exception as e:
        error_response = create_business_logic_error(f"Strategy creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=error_response.dict())


@router.get("/", response_model=List[StrategyResponse])
async def list_strategies(
    process_step: Optional[str] = Query(None),
    tool_type: Optional[str] = Query(None),
    lifecycle_state: Optional[str] = Query(None),
    service: StrategyService = Depends(get_strategy_service)
):
    """List strategies with optional filters."""
    try:
        lifecycle_filter = None
        if lifecycle_state:
            lifecycle_filter = StrategyLifecycle(lifecycle_state)
        
        definitions = service.list_strategies(
            process_step=process_step,
            tool_type=tool_type,
            lifecycle_state=lifecycle_filter
        )
        
        return [StrategyResponse.from_definition(d) for d in definitions]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{strategy_id}", response_model=Dict[str, Any], responses={404: {"model": NotFoundErrorResponse}})
async def get_strategy(
    strategy_id: str,
    version: Optional[str] = Query(None),
    service: StrategyService = Depends(get_strategy_service)
):
    """Get detailed strategy definition."""
    try:
        definition = service.get_strategy(strategy_id, version)
        if definition is None:
            error_response = create_not_found_error("Strategy", strategy_id)
            raise HTTPException(status_code=404, detail=error_response.dict())
        
        return definition.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        error_response = create_business_logic_error(f"Failed to retrieve strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=error_response.dict())


@router.put("/{strategy_id}", response_model=StrategyResponse, responses={404: {"model": NotFoundErrorResponse}, 400: {"model": ValidationErrorResponse}})
async def update_strategy(
    strategy_id: str,
    request: StrategyUpdateRequest,
    service: StrategyService = Depends(get_strategy_service)
):
    """Update strategy definition."""
    try:
        definition = service.update_strategy(strategy_id, request.dict(exclude_unset=True))
        if definition is None:
            error_response = create_not_found_error("Strategy", strategy_id)
            raise HTTPException(status_code=404, detail=error_response.dict())
        
        return StrategyResponse.from_definition(definition)
    except HTTPException:
        raise
    except ValueError as e:
        error_response = create_validation_error(str(e))
        raise HTTPException(status_code=400, detail=error_response.dict())
    except Exception as e:
        error_response = create_business_logic_error(f"Strategy update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=error_response.dict())


@router.post("/{strategy_id}/clone", response_model=StrategyResponse)
async def clone_strategy(
    strategy_id: str,
    new_name: str,
    author: str,
    service: StrategyService = Depends(get_strategy_service)
):
    """Clone an existing strategy."""
    try:
        definition = service.clone_strategy(strategy_id, new_name, author)
        if definition is None:
            raise HTTPException(status_code=404, detail="Source strategy not found")
        
        return StrategyResponse.from_definition(definition)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{strategy_id}/promote")
async def promote_strategy(
    strategy_id: str,
    user: str,
    service: StrategyService = Depends(get_strategy_service)
):
    """Promote strategy to next lifecycle stage."""
    try:
        success = service.promote_strategy(strategy_id, user)
        if not success:
            raise HTTPException(status_code=400, detail="Cannot promote strategy")
        
        return {"message": "Strategy promoted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{strategy_id}/simulate", response_model=SimulationResult, responses={404: {"model": NotFoundErrorResponse}, 400: {"model": ValidationErrorResponse}})
async def simulate_strategy(
    strategy_id: str,
    request: SimulationRequest,
    service: StrategyService = Depends(get_strategy_service)
):
    """Simulate strategy execution and return results."""
    try:
        result = service.simulate_strategy(
            strategy_id=strategy_id,  # Use path parameter instead of request body
            wafer_map_data=request.wafer_map_data,
            process_parameters=request.process_parameters,
            tool_constraints=request.tool_constraints
        )
        
        return SimulationResult(**result)
    except ValueError as e:
        # Handle strategy not found or validation errors
        if "not found" in str(e).lower():
            error_response = create_not_found_error("Strategy", strategy_id)
            raise HTTPException(status_code=404, detail=error_response.dict())
        else:
            error_response = create_validation_error(str(e))
            raise HTTPException(status_code=400, detail=error_response.dict())
    except Exception as e:
        error_response = create_business_logic_error(f"Simulation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=error_response.dict())


@router.get("/{strategy_id}/versions")
async def get_strategy_versions(
    strategy_id: str,
    service: StrategyService = Depends(get_strategy_service)
):
    """Get all versions of a strategy."""
    try:
        versions = service.get_strategy_versions(strategy_id)
        return [
            {
                "version": v.version,
                "created_at": v.created_at,
                "created_by": v.created_by,
                "changelog": v.changelog,
                "is_active": v.is_active
            }
            for v in versions
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    service: StrategyService = Depends(get_strategy_service)
):
    """Delete (deprecate) a strategy."""
    try:
        success = service.delete_strategy(strategy_id)
        if not success:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        return {"message": "Strategy deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))