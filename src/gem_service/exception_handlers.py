from fastapi import Request
from fastapi.responses import JSONResponse

from .exceptions import GemAlreadyExistsError, GemNotFoundError


async def gem_already_exists_handler(
    request: Request, exc: GemAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def gem_not_found_handler(
    request: Request, exc: GemNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})
