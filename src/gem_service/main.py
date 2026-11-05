from fastapi import FastAPI
from .routers.gems import router as gem_router

app = FastAPI(title="GemScout | Gem Service")

app.include_router(gem_router)