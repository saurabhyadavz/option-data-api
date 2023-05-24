from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = r"sqlite+aiosqlite:///C:\Users\DeGenOne\Downloads\truedata\truedata_options_copy_2" \
               r"\truedata_options_copy.db"
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"timeout": 50}
)

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
