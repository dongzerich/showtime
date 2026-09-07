# JMeter 压测脚本

## 文件说明

| 文件 | 说明 |
|------|------|
| `showtime_load_test.jmx` | JMeter 主压测脚本（登录→锁座→下单完整链路） |
| `test_users.csv` | 测试用户数据（账号/密码，共 100 个） |
| `seed_users.py` | 批量创建测试账号（Python，尊重 register 限流） |

## 压测链路

每个虚拟用户一轮迭代执行：**登录 → 锁座 → 下单**。

- 每个线程固定使用 `seatId = SEAT_MIN + 线程号 - 1`，并发下不同线程不抢同一座位；
- 下单使用锁座接口返回的真实 `lockToken`，不伪造锁令牌。

## 前置条件

1. 后端已启动（默认 `http://localhost:5146`，可用 `-JDOMAIN/-JPORT/-JPROTOCOL` 覆盖）。
2. 场次与座位：`SESSION_ID`（默认 1）场次存在，且包含 `SEAT_MIN .. SEAT_MIN+THREADS-1`
   这些**未售座位**；`PRICE_STRATEGY_ID`（默认 1）是该场次有效的定价策略。
3. 测试账号：CSV 中账号在真实库不存在会导致登录 401，先建号：

```bash
cd test/jmeter
# 建 100 个（与 CSV 一致）。register 限流 3 次/分钟/IP，约需 35 分钟；本地冒烟可用 --count 10
python3 seed_users.py --count 100
```

## 单机运行

```bash
cd test/jmeter
jmeter -n -t showtime_load_test.jmx -JTHREADS=50 -JLOOPS=1 -l results.jtl -e -o report/
```

常用参数：`-JTHREADS`、`-JLOOPS`、`-JRAMP_UP`、`-JSESSION_ID`、`-JSEAT_MIN`、`-JPRICE_STRATEGY_ID`。

> 注意：login 接口限流 **5 次/分钟/IP**，单机大并发必然 429；单机建议小线程冒烟，
> 正式压测请用下面的分布式方式由多台机器分摊。

## 分布式运行（多机分摊限流与流量）

1. 每台 slave 启动 `jmeter-server`，并给不同 slave 配不同的 `SEAT_MIN` 起点，避免抢同一批座位：

```bash
# slave1: 使用 1..THREADS
jmeter-server -JSEAT_MIN=1
# slave2: 使用 201..200+THREADS（按实际座位数调整偏移）
jmeter-server -JSEAT_MIN=201
```

2. master 汇总执行（`THREADS` 为每台 slave 的线程数，座位范围需覆盖 `THREADS × slave 数`）：

```bash
jmeter -n -t showtime_load_test.jmx -R slave1,slave2 -JTHREADS=200 -l results.jtl -e -o report/
```

> `-J` 参数只作用于本机；slave 各自的 `SEAT_MIN` 需在其启动参数中配置。

## 常见问题

- 登录 401：CSV 账号未创建，先运行 `seed_users.py`。
- 登录 429：login 限流 5 次/分钟/IP，降低 `THREADS` 或改为多机压测。
- 锁座 4xx：`SESSION_ID`/座位号不存在、座位已售或已被他人锁定。
- 下单 4xx：`lockToken` 过期或座位已被买走；确认 `SEAT_MIN` 覆盖范围足够大。
- 失败遗留的 ACTIVE 锁默认 600 秒自动过期；重跑前可等待或换一批 `SEAT_MIN`。
