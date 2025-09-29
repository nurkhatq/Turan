# app/core/exceptions.py
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BusinessCRMException(Exception):
    """Base exception for the CRM system."""
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(BusinessCRMException):
    """Authentication related errors."""
    pass


class AuthorizationError(BusinessCRMException):
    """Authorization related errors."""
    pass


class IntegrationError(BusinessCRMException):
    """Integration related errors."""
    pass


class ValidationError(BusinessCRMException):
    """Validation related errors."""
    pass


class NotFoundError(BusinessCRMException):
    """Resource not found errors."""
    pass


class ConflictError(BusinessCRMException):
    """Resource conflict errors."""
    pass


# HTTP Exception helpers
def create_http_exception(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create HTTP exception with structured error response."""
    return HTTPException(
        status_code=status_code,
        detail={
            "message": message,
            "details": details or {}
        }
    )


def authentication_exception(message: str = "Authentication required") -> HTTPException:
    return create_http_exception(status.HTTP_401_UNAUTHORIZED, message)


def authorization_exception(message: str = "Access denied") -> HTTPException:
    return create_http_exception(status.HTTP_403_FORBIDDEN, message)


def not_found_exception(message: str = "Resource not found") -> HTTPException:
    return create_http_exception(status.HTTP_404_NOT_FOUND, message)


def validation_exception(
    message: str = "Validation error", 
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    return create_http_exception(status.HTTP_422_UNPROCESSABLE_ENTITY, message, details)


def conflict_exception(message: str = "Resource conflict") -> HTTPException:
    return create_http_exception(status.HTTP_409_CONFLICT, message)


def integration_exception(message: str = "Integration error") -> HTTPException:
    return create_http_exception(status.HTTP_502_BAD_GATEWAY, message)