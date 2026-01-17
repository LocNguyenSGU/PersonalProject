class AppException(Exception):
    """Base application exception"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class GA4Error(AppException):
    """GA4 API errors"""
    pass

class LLMError(AppException):
    """LLM provider errors"""
    pass

class DatabaseError(AppException):
    """Database errors"""
    pass

class AuthError(AppException):
    """Authentication errors"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)
