class AuthError(Exception):
    message: str
    error_code: str
    status_code: int

    def __init__(self, message: str, error_code: str, status_code: int = 400) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class UserAlreadyExistsError(AuthError):
    def __init__(self, message: str = "User already exists") -> None:
        super().__init__(message, error_code="USER_ALREADY_EXISTS", status_code=409)


class InvalidCredentialsError(AuthError):
    def __init__(self, message: str = "Incorrect email or password") -> None:
        super().__init__(message, error_code="INVALID_CREDENTIALS", status_code=401)


class UserInactiveError(AuthError):
    def __init__(self, message: str = "User account is deactivated") -> None:
        super().__init__(message, error_code="USER_INACTIVE", status_code=403)


class DefaultRoleNotFoundError(RuntimeError):
    def __init__(
        self, message: str = "Critical configuration error: Default user role not found"
    ) -> None:
        super().__init__(message)


class InvalidTokenError(AuthError):
    def __init__(self, message: str = "Invalid or expired token") -> None:
        super().__init__(message, error_code="INVALID_TOKEN", status_code=401)
