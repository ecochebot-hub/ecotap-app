import asyncio
from database import db

async def test():
    print("Testing database connection...")
    await db.init_db()
    print("✅ Database connected!")

    # Test user registration
    success = await db.register_user(
        user_id=123456789,
        username="testuser",
        first_name="Test",
        last_name="User"
    )
    print(f"✅ User registration: {success}")

    # Test get progress
    progress = await db.get_user_progress(123456789)
    print(f"✅ User progress: {progress}")

    await db.close()
    print("✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test())
