import asyncio
from database import engine


async def check_connection():
    async with engine.connect() as conn:
        print("Connection Successful! Database engine is ready.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_connection())
