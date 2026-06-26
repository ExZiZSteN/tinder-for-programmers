import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from sqlalchemy import select
from app.core.database import async_session
from app.models.skill import Skill
from app.models.base import Base
from app.models.user import User
from app.models.project import Project
from app.models.user_skill import UserSkill
from app.models.project_skill import ProjectSkill
from app.models.project_member import ProjectMember
from app.models.swipe import Swipe
from app.models.match import Match
from app.models.message import Message
from app.models.notification import Notification
from app.models.file import File
from app.models.refresh_token import RefreshToken

POPULAR_SKILLS = [
    # Языки программирования
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "PHP", "Ruby",
    
    # Frontend
    "React", "Vue.js", "Angular", "Svelte", "Next.js", "HTML", "CSS", "Tailwind CSS",
    
    # Backend
    "Node.js", "Django", "FastAPI", "Flask", "Spring Boot", "Express.js", "NestJS",
    
    # Базы данных
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Elasticsearch",
    
    # DevOps
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Linux", "Nginx",
    
    # Мобильная разработка
    "React Native", "Flutter", "iOS", "Android", "Swift", "Kotlin",
    
    # Data Science / ML
    "Machine Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Jupyter",
    
    # Инструменты
    "Git", "GitHub", "GitLab", "Jira", "Figma", "Postman",
    
    # Методологии
    "Agile", "Scrum", "Kanban", "TDD",
]


async def seed_skills():
    async with async_session() as db:
        # Проверяем, есть ли уже навыки
        result = await db.execute(select(Skill))
        existing = result.scalars().all()
        
        if existing:
            print(f"⚠ В базе уже есть {len(existing)} навыков. Пропускаем seed.")
            return
        
        print(f"🌱 Создаём {len(POPULAR_SKILLS)} популярных навыков...")
        
        for skill_name in POPULAR_SKILLS:
            skill = Skill(name=skill_name)
            db.add(skill)
        
        await db.commit()
        print(f"✅ Создано {len(POPULAR_SKILLS)} навыков!")


if __name__ == "__main__":
    asyncio.run(seed_skills())