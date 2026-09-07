

## 文件6：`test/security/owasp_test.py`

```python
#!/usr/bin/env python3
import requests
import json
import time
from urllib.parse import quote

BASE_URL = "http://localhost:5146"
TEST_USER = {"account": "e2e_test_001", "password": "Test123456"}

print("=" * 60)
print("OWASP Top 10 安全测试 - Showtime")
print("=" * 60)

# ============================================================
# 1. A01: 失效的访问控制
# ============================================================
print("\n[1] A01: 失效的访问控制")

# 无 token 访问订单列表
resp = requests.get(f"{BASE_URL}/api/orders")
print(f"  无 token 访问 /api/orders: {resp.status_code} (预期 401)")
assert resp.status_code == 401, "❌ 应返回 401"

# 无 token 访问用户中心
resp = requests.get(f"{BASE_URL}/api/users/me")
print(f"  无 token 访问 /api/users/me: {resp.status_code} (预期 401)")
assert resp.status_code == 401, "❌ 应返回 401"

print("  ✅ 访问控制测试通过")

# ============================================================
# 2. A03: SQL 注入
# ============================================================
print("\n[2] A03: SQL 注入")

payloads = ["' OR '1'='1", "admin'--", "'; DROP TABLE sys_user; --"]
for payload in payloads:
    resp = requests.get(f"{BASE_URL}/api/client/shows?keyword={quote(payload)}")
    if "ORA-" in resp.text or "SQL" in resp.text.upper():
        print(f"  ⚠️ 可能存在 SQL 注入: {payload[:20]}")
    else:
        print(f"  ✅ 安全: {payload[:20]}")

# ============================================================
# 3. A07: 识别与认证失败 - 暴力破解 + 429限流
# ============================================================
print("\n[3] A07: 暴力破解防护")

success_count = 0
rate_limit_triggered = False

for i in range(15):
    resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"account": TEST_USER["account"], "password": f"wrong_{i}"}
    )
    if resp.status_code == 200:
        success_count += 1
    elif resp.status_code == 429:
        rate_limit_triggered = True
        print(f"  尝试 {i+1}: {resp.status_code} (速率限制触发 ✅)")

if success_count == 0:
    print("  ✅ 暴力破解防护有效")
else:
    print(f"  ⚠️ 有 {success_count} 次成功登录")

if rate_limit_triggered:
    print("  ✅ 速率限制生效 (429)")
else:
    print("  ⚠️ 速率限制未触发，建议检查限流配置")

# ============================================================
# 4. A03: CSRF 测试
# ============================================================
print("\n[4] CSRF 测试 (无 CSRF Token)")

# 先登录获取 token
login_resp = requests.post(
    f"{BASE_URL}/api/auth/login",
    json=TEST_USER
)
token = login_resp.json().get("data", {}).get("accessToken")

if token:
    # 不带 CSRF Token 的请求
    resp = requests.post(
        f"{BASE_URL}/api/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={"sessionId": 1, "items": []}
    )
    print(f"  无 CSRF Token 请求: {resp.status_code}")
    # CSRF 保护通常返回 403
    if resp.status_code == 403:
        print("  ✅ CSRF 保护有效")
    else:
        print("  ⚠️ 建议检查 CSRF 防护配置")

# ============================================================
# 5. XSS - 跨站脚本
# ============================================================
print("\n[5] XSS")

xss_payloads = ["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>"]
for payload in xss_payloads:
    resp = requests.get(f"{BASE_URL}/api/client/shows?keyword={quote(payload)}")
    if payload in resp.text:
        print(f"  ⚠️ 可能存在 XSS: {payload[:20]}")
    else:
        print(f"  ✅ 安全: {payload[:20]}")

# ============================================================
# 6. 敏感信息泄露
# ============================================================
print("\n[6] 敏感信息泄露")

resp = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"account": "", "password": ""}
)
if "stacktrace" in resp.text.lower() or "inner exception" in resp.text.lower():
    print("  ⚠️ 错误响应泄露堆栈信息")
else:
    print("  ✅ 错误响应安全")

print("\n" + "=" * 60)
print("安全测试完成")