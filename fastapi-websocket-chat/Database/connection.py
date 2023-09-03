from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from Models.sqlData import Base
from starlette.config import Config


config = Config(".env")
SECRET_KEY = config.get("SECRET_KEY")
SQLALCHEMY_DATABASE_URL = config.get("SQLALCHEMY_DATABASE_URL")
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
