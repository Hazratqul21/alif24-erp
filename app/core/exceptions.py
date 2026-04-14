from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=message)


class NotFoundError(AppError):
    def __init__(self, resource: str = "Resurs"):
        super().__init__(f"{resource} topilmadi", status_code=status.HTTP_404_NOT_FOUND)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Avtorizatsiya talab qilinadi"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Ruxsat yo'q"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class TenantNotFoundError(AppError):
    def __init__(self):
        super().__init__("Maktab topilmadi yoki faol emas", status_code=status.HTTP_404_NOT_FOUND)


class TenantBlockedError(AppError):
    def __init__(self):
        super().__init__("Maktab bloklangan", status_code=status.HTTP_403_FORBIDDEN)


class TenantExpiredError(AppError):
    def __init__(self):
        super().__init__("Obuna muddati tugagan", status_code=status.HTTP_403_FORBIDDEN)


class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ConflictError(AppError):
    def __init__(self, message: str = "Resurs allaqachon mavjud"):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)
