class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class CodeAlreadyUsedError(Exception):
    pass


class CodeExpiredError(Exception):
    pass


class AttemptsError(Exception):
    pass
