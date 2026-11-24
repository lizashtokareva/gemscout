class GemAlreadyExistsError(Exception):
    pass


class GemNotFoundError(Exception):
    pass


class IncorrectPriceError(Exception):
    pass


class GemPermissionDeniedError(Exception):
    pass


class IdempotencyRecordNotFoundError(Exception):
    pass
