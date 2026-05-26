from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False) -> None:
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )


async def get_async_psql_session() -> AsyncGenerator[AsyncSession]:
    async with db_helper.session_factory() as session:
        yield session


db_helper = DatabaseHelper(url=settings.db.get_database_URL, echo=settings.db.echo)
