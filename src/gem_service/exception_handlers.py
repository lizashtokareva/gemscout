from fastapi import Request
from fastapi.responses import JSONResponse

from .exceptions import (
    GemAlreadyExistsError,
    GemNotFoundError,
    GemPermissionDeniedError,
    IncorrectPriceError,
)


async def gem_already_exists_handler(
    request: Request, exc: GemAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def gem_not_found_handler(
    request: Request, exc: GemNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def incorrect_price_error_handler(
    request: Request, exc: IncorrectPriceError
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def gem_permission_denied_handler(
    request: Request, exc: GemPermissionDeniedError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})
