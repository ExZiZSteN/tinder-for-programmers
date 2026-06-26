# scripts/check_r0.py
"""Скрипт проверки R0 (Foundation).

Проверяет:
- Health endpoint
- Регистрация пользователя
- Логин
- Получение профиля /me
- Создание проекта
- Получение проекта
- Список проектов
"""
import asyncio
import httpx


BASE_URL = "http://localhost:8000"


async def test_r0():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Health check
        print("1. Health check...")
        r = await client.get(f"{BASE_URL}/")
        assert r.status_code == 200, f"Root failed: {r.text}"
        print(f"   ✓ Root: {r.json()}")
        
        # 2. Регистрация
        print("\n2. Регистрация...")
        r = await client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": "r0_test@example.com",
                "password": "testpass123",
                "full_name": "R0 Test User",
            },
        )
        if r.status_code == 409:
            print("   ⚠ User already exists, продолжаем с логином")
        else:
            assert r.status_code == 201, f"Register failed: {r.text}"
            print(f"   ✓ Registered: {r.json().get('user_id')}")
        
        # 3. Логин
        print("\n3. Логин...")
        r = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "r0_test@example.com",
                "password": "testpass123",
            },
        )
        assert r.status_code == 200, f"Login failed: {r.text}"
        tokens = r.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        print(f"   ✓ Got tokens (access: {access_token[:20]}...)")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 4. /me
        print("\n4. GET /me...")
        r = await client.get(f"{BASE_URL}/api/users/me", headers=headers)
        assert r.status_code == 200, f"Get me failed: {r.text}"
        me = r.json()
        print(f"   ✓ User: {me.get('email')}, id={me.get('id')}")
        
        # 5. Создание проекта
        print("\n5. POST /projects...")
        r = await client.post(
            f"{BASE_URL}/api/projects",
            headers=headers,
            json={
                "title": "R0 Test Project",
                "description": "Тестовый проект для проверки фундамента",
                "format": "remote",
                "payment_type": "volunteer",
                "skill_ids": [],
            },
        )
        assert r.status_code == 201, f"Create project failed: {r.text}"
        project = r.json()
        project_id = project["id"]
        print(f"   ✓ Project created: id={project_id}")
        
        # 6. Получение проекта
        print("\n6. GET /projects/{id}...")
        r = await client.get(f"{BASE_URL}/api/projects/{project_id}")
        assert r.status_code == 200, f"Get project failed: {r.text}"
        print(f"   ✓ Got project: {r.json().get('title')}")
        
        # 7. Список проектов
        print("\n7. GET /projects (list)...")
        r = await client.get(f"{BASE_URL}/api/projects")
        assert r.status_code == 200, f"List projects failed: {r.text}"
        projects = r.json()
        print(f"   ✓ Listed {len(projects)} projects")
        
        # 8. Refresh token
        print("\n8. POST /auth/refresh...")
        r = await client.post(
            f"{BASE_URL}/api/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        if r.status_code == 200:
            print(f"   ✓ Token refreshed")
        else:
            print(f"   ⚠ Refresh failed: {r.status_code} (may be expected)")
        
        print("\n" + "=" * 50)
        print("✅ R0 (Foundation) CHECK PASSED!")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_r0())
