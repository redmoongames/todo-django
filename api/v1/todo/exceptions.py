class APIError(Exception):
    def __init__(self, message: str, status: int = 400):
        self.message = message
        self.status = status
        super().__init__(message)


class NotFoundError(APIError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status=404)


class PermissionError(APIError):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status=403)


class ValidationError(APIError):
    def __init__(self, message: str = "Invalid data"):
        super().__init__(message, status=400)


class ConflictError(APIError):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status=409) 