import asyncio
from sqlmodel import Session, select
from app.database.session import create_async_engine  # Ensure this imports your 'create_async_engine'
from app.database.models import Tag

# If your engine is asynchronous (common in FastAPI),
# you need to use an async session for the test.
from sqlmodel.ext.asyncio.session import AsyncSession


async def test_db_connection():
    # Use AsyncSession for async engines
    async with AsyncSession(create_async_engine) as session:
        statement = select(Tag)
        results = await session.exec(statement)
        tags = results.all()

        if not tags:
            print("Connection successful, but the 'tag' table is empty.")
        else:
            print(f"Success! Found {len(tags)} tags:")
            for tag in tags:
                print(f"- {tag.name}: {tag.instruction}")


if __name__ == "__main__":
    asyncio.run(test_db_connection())