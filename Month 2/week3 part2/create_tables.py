import asyncio
from database import engine, Base
from models import Product  # noqa: F401


async def init_db():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)

        await conn.run_sync(Base.metadata.create_all)

    print("Tables Created sucessfully")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
