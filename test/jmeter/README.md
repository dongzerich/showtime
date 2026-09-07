# JMeter 压测脚本

## 文件说明

| 文件 | 说明 |
|------|------|
| `showtime_load_test.jmx` | JMeter 主压测脚本 |
| `test_users.csv` | 测试用户数据（账号/密码） |

## 运行方式

```bash
# 进入目录
cd test/jmeter

# 运行压测（500并发）
jmeter -n -t showtime_load_test.jmx -l results.jtl -e -o report/

# 不同并发级别
jmeter -n -t showtime_load_test.jmx -JTHREADS=500 -l results_500.jtl -e -o report_500/
jmeter -n -t showtime_load_test.jmx -JTHREADS=1000 -l results_1000.jtl -e -o report_1000/
jmeter -n -t showtime_load_test.jmx -JTHREADS=2000 -l results_2000.jtl -e -o report_2000/