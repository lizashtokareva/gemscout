import asyncio
import os
import selectors
import sys

import pytest
import pytest_asyncio
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from typing_extensions import AsyncIterator


def pytest_asyncio_loop_factories(
    config: pytest.Config,
    item: pytest.Item,
) -> dict:
    if sys.platform == "win32":
        return {
            "selector": lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
        }

    return {"default": asyncio.new_event_loop}


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    database_url = os.environ.get("AUTH_TEST_DATABASE_URL")

    if not database_url:
        raise RuntimeError("AUTH_TEST_DATABASE_URL is not configured")

    if make_url(database_url).database != "auth_gemscout_test_db":
        raise RuntimeError("Tests must use the test database!")

    engine = create_async_engine(database_url)

    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()

            try:
                async with AsyncSession(
                    bind=connection,
                    expire_on_commit=False,
                    join_transaction_mode="create_savepoint",
                ) as session:
                    yield session
            finally:
                await transaction.rollback()
    finally:
        await engine.dispose()
