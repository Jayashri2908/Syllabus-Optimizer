"""Custom exceptions for SCDO"""


class SCDOException(Exception):
    """Base exception for SCDO"""
    def __init__(self, message: str, error_code: str = "SCDO_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(SCDOException):
    """Invalid input data"""
    def __init__(self, message: str):
        super().__init__(message, error_code="VALIDATION_ERROR", status_code=400)


class AIUnavailableException(SCDOException):
    """AI model unavailable"""
    def __init__(self, message: str = "AI model unavailable"):
        super().__init__(message, error_code="AI_UNAVAILABLE", status_code=503)


class ParseException(SCDOException):
    """Syllabus parsing failed"""
    def __init__(self, message: str):
        super().__init__(message, error_code="PARSE_ERROR", status_code=422)


class OptimizationException(SCDOException):
    """Optimization failed"""
    def __init__(self, message: str):
        super().__init__(message, error_code="OPTIMIZATION_ERROR", status_code=500)


class ExportException(SCDOException):
    """Export failed"""
    def __init__(self, message: str):
        super().__init__(message, error_code="EXPORT_ERROR", status_code=500)
