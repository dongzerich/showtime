#!/usr/bin/env python3
import requests
import time

BASE_URL = "http://localhost:5146"

def create_users(count=100):
    for i in range(1, count + 1):
        username = f"e2e_test_{i:03d}"
        phone = f"138{10000000 + i:08d}"
        email = f"{username}@example.com"

        try:
            resp = requests.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "username": username,
                    "password": "Test123456",
                    "phone": phone,
                    "email": email
                },
                timeout=5
            )
            if resp.status_code in (201, 409):
                print(f"✅ {username} created (status: {resp.status_code})")
            else:
                print(f"⚠️ {username} failed: {resp.status_code} - {resp.text[:50]}")
        except Exception as e:
            print(f"❌ {username} error: {e}")

        time.sleep(0.2)  # 避免触发限流

    print(f"\n✅ 完成！共创建 {count} 个测试账号")

if __name__ == "__main__":
    create_users(100)