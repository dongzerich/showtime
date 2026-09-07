
---

### 文件 4：`test/security/owasp_test.py`

```python
#!/usr/bin/env python3
import requests
import json
from urllib.parse import quote

BASE_URL = "http://localhost:5146"
TEST_USER = {"account": "e2e_test_001", "password": "Test123456"}

print("=" * 60)
print("OWASP Top 10 安全测试 - Showtime")
print("=" * 60)

# 1. A01: 失效的访问控制
print("\n[1] A01: 失效的访问控制")
resp = requests.get(f"{BASE_URL}/api/orders")
print(f"  无 token 访问 /api/orders: {resp.status_code}")
assert resp.status_code == 401, "应返回 401"

# 2. A03: SQL 注入
print("\n[2] A03: SQL 注入")
payloads = ["' OR '1'='1", "admin'--", "'; DROP TABLE sys_user; --"]
for payload in payloads:
    resp = requests.get(f"{BASE_URL}/api/shows?keyword={quote(payload)}")
    if "ORA-" in resp.text or "SQL" in resp.text.upper():
        print(f"  ⚠️ 可能存在 SQL 注入: {payload[:20]}")
    else:
        print(f"  ✅ 安全: {payload[:20]}")

# 3. A07: 暴力破解防护
print("\n[3] A07: 暴力破解防护")
success_count = 0
for i in range(10):
    resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"account": TEST_USER["account"], "password": f"wrong_{i}"}
    )
    if resp.status_code == 200:
        success_count += 1
    print(f"  尝试 {i+1}: {resp.status_code}")
if success_count == 0:
    print("  ✅ 暴力破解防护有效")
else:
    print(f"  ⚠️ 有 {success_count} 次成功登录")

# 4. XSS
print("\n[4] XSS")
xss_payloads = ["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>"]
for payload in xss_payloads:
    resp = requests.get(f"{BASE_URL}/api/shows?keyword={quote(payload)}")
    if payload in resp.text:
        print(f"  ⚠️ 可能存在 XSS: {payload[:20]}")
    else:
        print(f"  ✅ 安全: {payload[:20]}")

print("\n" + "=" * 60)
print("安全测试完成")