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


class IncorrectTypeError(Exception):
    pass


class ImageNotFoundError(Exception):
    pass


class ImageTooLargeError(Exception):
    pass


class ImageAlreadyExistsError(Exception):
    pass
