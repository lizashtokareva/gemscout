from fastapi import FastAPI

from gem_service.exception_handlers import (
    gem_already_exists_handler,
    gem_not_found_handler,
)
from gem_service.exceptions import GemAlreadyExistsError, GemNotFoundError
from gem_service.routers.gems import router as gem_router

app = FastAPI(title="GemScout | Gem Service")

app.include_router(gem_router)

app.add_exception_handler(GemAlreadyExistsError, gem_already_exists_handler)

app.add_exception_handler(GemNotFoundError, gem_not_found_handler)
