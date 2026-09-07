# JMeter 压测脚本

## 文件说明

| 文件 | 说明 |
|------|------|
| `showtime_load_test.jmx` | JMeter 主压测脚本 |
| `test_users.csv` | 测试用户数据 |
| `seed_users.py` | 批量创建测试账号（Python） |
| `seed_users.sh` | 批量创建测试账号（Shell） |

## 前置条件

### 1. 创建测试账号

```bash
# Python 版本
python3 seed_users.py

# 或 Shell 版本（Git Bash / WSL）
bash seed_users.sh