class AuthError(Exception):
    """All auth errors"""

    pass


class UserAlreadyExistsError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass


class UserInactiveError(AuthError):
    pass


class DefaultRoleNotFoundError(AuthError):
    pass
