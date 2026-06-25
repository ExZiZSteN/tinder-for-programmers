import asyncio
import sys

# ⚠️ КРИТИЧНО для Windows + asyncpg
# Должно быть вызвано ДО asyncio.run()
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import text
from app.core.database import async_session
from app.repositories.skill import SkillRepository
from app.repositories.user import UserRepository


async def main():
    print("🔌 Проверяю подключение к БД...")
    
    try:
        async with async_session() as session:
            result = await session.execute(text("SELECT 1 AS test"))
            value = result.scalar()
            print(f"✅ Подключение работает! Результат SELECT 1: {value}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {type(e).__name__}: {e}")
        return
    
    print("\n🔌 Проверяю репозитории...")
    try:
        async with async_session() as session:
            skill_repo = SkillRepository(session)
            skill = await skill_repo.find_or_create("Python")
            print(f"✓ Skill: {skill.name} (id={skill.id})")
            
            skill2 = await skill_repo.find_or_create("Python")
            assert skill.id == skill2.id
            print("✓ find_or_create возвращает существующий")
            
            user_repo = UserRepository(session)
            user = await user_repo.get_by_email("notexist@example.com")
            assert user is None
            print("✓ get_by_email возвращает None для несуществующего")
            
            # Откатить тестовые данные
            await session.rollback()
            print("✓ Тестовые данные откачены")
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🎉 Все проверки пройдены!")


if __name__ == "__main__":
    asyncio.run(main())