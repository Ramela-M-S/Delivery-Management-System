import asyncio
from sqlalchemy import text
from app.database.session import engine


async def factory_reset_db():
    # .begin() automatically commits the transaction if no errors happen
    async with engine.begin() as conn:
        print("⚠️  DEMOLISHING THE DATABASE SCHEMA...")
        # This instantly vaporizes every table, every row, every sequence,
        # and Alembic's hidden version-tracking table.
        await conn.execute(text("DROP SCHEMA public CASCADE;"))

        print("🌱 RE-POURING THE CONCRETE FOUNDATION...")
        await conn.execute(text("CREATE SCHEMA public;"))

        print("✨ DATABASE IS NOW A 100% BLANK VOID.")


if __name__ == "__main__":
    asyncio.run(factory_reset_db())