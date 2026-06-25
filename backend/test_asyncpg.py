import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import asyncpg


async def main():
    try:
        conn = await asyncpg.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres",
            database="tinder_devs",
        )
        version = await conn.fetchval("SELECT version()")
        print(f"✅ CONNECTED via asyncpg!")
        print(f"PostgreSQL: {version[:50]}...")
        await conn.close()
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")


asyncio.run(main())