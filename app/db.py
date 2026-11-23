from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine,async_sessionmaker


DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session  
