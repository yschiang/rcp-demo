"""
Standardized error response models for consistent API error handling.
"""
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from enum import Enum


class ErrorType(str, Enum):
    """Error type categories for better error handling."""
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    AUTHORIZATION_ERROR = "authorization_error"
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    INTERNAL_ERROR = "internal_error"
    RATE_LIMIT_ERROR = "rate_limit_error"


class ErrorDetail(BaseModel):
    """Individual error detail."""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Machine-readable error code")


class StandardErrorResponse(BaseModel):
    """Standardized error response format for all API endpoints."""
    error: bool = Field(True, description="Always true for error responses")
    error_type: ErrorType = Field(..., description="Category of error")
    message: str = Field(..., description="Primary error message")
    details: List[ErrorDetail] = Field(default_factory=list, description="Detailed error information")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    timestamp: Optional[str] = Field(None, description="Error timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "error": True,
                "error_type": "validation_error",
                "message": "Strategy validation failed",
                "details": [
                    {
                        "field": "name",
                        "message": "Strategy name is required",
                        "code": "FIELD_REQUIRED"
                    }
                ],
                "request_id": "req_123456",
                "timestamp": "2025-07-13T16:47:12.123456"
            }
        }


class ValidationErrorResponse(StandardErrorResponse):
    """Specific error response for validation failures."""
    error_type: ErrorType = ErrorType.VALIDATION_ERROR


class NotFoundErrorResponse(StandardErrorResponse):
    """Specific error response for resource not found."""
    error_type: ErrorType = ErrorType.NOT_FOUND


class BusinessLogicErrorResponse(StandardErrorResponse):
    """Specific error response for business logic violations."""
    error_type: ErrorType = ErrorType.BUSINESS_LOGIC_ERROR


def create_validation_error(message: str, field_errors: List[Dict[str, str]] = None, request_id: str = None) -> StandardErrorResponse:
    """Create a standardized validation error response."""
    from datetime import datetime
    
    details = []
    if field_errors:
        for error in field_errors:
            details.append(ErrorDetail(
                field=error.get("field"),
                message=error.get("message", "Validation failed"),
                code=error.get("code", "VALIDATION_ERROR")
            ))
    
    return ValidationErrorResponse(
        message=message,
        details=details,
        request_id=request_id,
        timestamp=datetime.now().isoformat()
    )


def create_not_found_error(resource: str, identifier: str = None, request_id: str = None) -> StandardErrorResponse:
    """Create a standardized not found error response."""
    from datetime import datetime
    
    message = f"{resource} not found"
    if identifier:
        message += f" with identifier: {identifier}"
    
    return NotFoundErrorResponse(
        message=message,
        details=[ErrorDetail(
            message=message,
            code="NOT_FOUND"
        )],
        request_id=request_id,
        timestamp=datetime.now().isoformat()
    )


def create_business_logic_error(message: str, code: str = None, request_id: str = None) -> StandardErrorResponse:
    """Create a standardized business logic error response."""
    from datetime import datetime
    
    return BusinessLogicErrorResponse(
        message=message,
        details=[ErrorDetail(
            message=message,
            code=code or "BUSINESS_LOGIC_ERROR"
        )],
        request_id=request_id,
        timestamp=datetime.now().isoformat()
    )


def create_internal_error(message: str = "Internal server error", request_id: str = None) -> StandardErrorResponse:
    """Create a standardized internal error response."""
    from datetime import datetime
    
    return StandardErrorResponse(
        error_type=ErrorType.INTERNAL_ERROR,
        message=message,
        details=[ErrorDetail(
            message=message,
            code="INTERNAL_ERROR"
        )],
        request_id=request_id,
        timestamp=datetime.now().isoformat()
    )