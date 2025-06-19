from fastapi import HTTPException
from typing import Optional, Dict, Any


class MenuExplainerException(Exception):
    """Base exception for Menu Explainer application."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(MenuExplainerException):
    """Raised when a requested resource is not found."""
    pass


class ValidationError(MenuExplainerException):
    """Raised when data validation fails."""
    pass


class DatabaseError(MenuExplainerException):
    """Raised when database operations fail."""
    pass


class ConfigurationError(MenuExplainerException):
    """Raised when configuration is invalid."""
    pass


def restaurant_not_found(restaurant_name: str) -> HTTPException:
    """Create HTTPException for restaurant not found."""
    return HTTPException(
        status_code=404,
        detail={
            "error": "Restaurant not found",
            "message": f"Restaurant '{restaurant_name}' not found",
            "restaurant_name": restaurant_name
        }
    )


def section_not_found(restaurant_name: str, section_name: str) -> HTTPException:
    """Create HTTPException for section not found."""
    return HTTPException(
        status_code=404,
        detail={
            "error": "Section not found",
            "message": f"Section '{section_name}' not found in restaurant '{restaurant_name}'",
            "restaurant_name": restaurant_name,
            "section_name": section_name
        }
    )


def validation_error(message: str, field: Optional[str] = None) -> HTTPException:
    """Create HTTPException for validation errors."""
    detail = {
        "error": "Validation error",
        "message": message
    }
    if field:
        detail["field"] = field
    
    return HTTPException(status_code=400, detail=detail)


def internal_server_error(message: str = "Internal server error") -> HTTPException:
    """Create HTTPException for internal server errors."""
    return HTTPException(
        status_code=500,
        detail={
            "error": "Internal server error",
            "message": message
        }
    )