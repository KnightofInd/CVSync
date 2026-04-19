"""Custom exceptions for CVSync."""


class CVSyncError(Exception):
    """Base exception for all CVSync errors."""


class ValidationError(CVSyncError):
    """Raised when required input validation fails."""


class IngestionError(CVSyncError):
    """Raised when document ingestion fails."""
