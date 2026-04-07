"""
Custom exceptions following DDD patterns
"""


class MRAnalyticsException(Exception):
    """Base exception for MR Analytics"""
    pass


class ConfigurationError(MRAnalyticsException):
    """Configuration error"""
    pass


class APIError(MRAnalyticsException):
    """API communication error"""
    
    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(MRAnalyticsException):
    """Resource not found"""
    
    def __init__(self, resource_type: str, resource_id: str):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} with ID {resource_id} not found")


class DatabaseError(MRAnalyticsException):
    """Database operation error"""
    pass


class DomainValidationError(MRAnalyticsException):
    """Domain validation error"""
    
    def __init__(self, field_name: str, message: str):
        self.field_name = field_name
        super().__init__(f"Validation error for {field_name}: {message}")


class RepositoryError(MRAnalyticsException):
    """Repository operation error"""
    pass


class UnitOfWorkError(MRAnalyticsException):
    """Unit of Work operation error"""
    pass


class UseCaseError(MRAnalyticsException):
    """Use case execution error"""
    pass


class MetricsCalculationError(MRAnalyticsException):
    """Metrics calculation error"""
    pass


class VCSError(MRAnalyticsException):
    """Version Control System error"""
    pass


class AuthenticationError(VCSError):
    """VCS authentication error"""
    pass


class RateLimitError(VCSError):
    """VCS rate limit error"""
    
    def __init__(self, message: str, retry_after: int | None = None):
        self.retry_after = retry_after
        super().__init__(message)
