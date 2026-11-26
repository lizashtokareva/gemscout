from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from rag_service.app.core.config import settings


class QdrantStorage:
    def __init__(self) -> None:
        self.client = AsyncQdrantClient(url=settings.qdrant_url)

    async def ensure_collection(self) -> None:
        exists = await self.client.collection_exists(
            collection_name=settings.qdrant_collection
        )
        if not exists:
            await self.client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                ),
            )

    async def upsert_gem(
        self,
        gem_id: int,
        vector: list[float],
        name: str,
        price: str,
    ) -> None:
        await self.client.upsert(
            collection_name=settings.qdrant_collection,
            points=[
                PointStruct(
                    id=gem_id,
                    vector=vector,
                    payload={"name": name, "price": price},
                )
            ],
            wait=True,
        )
