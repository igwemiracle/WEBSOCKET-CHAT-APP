from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from Models.sqlData import Base
from starlette.config import Config


config = Config(".env")
SECRET_KEY = b"HI5HL3V3L$3CR3T"
# SQLALCHEMY_DATABASE_URL = config.get("SQLALCHEMY_DATABASE_URL")
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///chat.sql"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL,
                             connect_args={"check_same_thread": True})
SessionLocal = async_sessionmaker(engine)


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
