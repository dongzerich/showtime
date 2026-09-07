

## 文件8：`test/performance/compare_results.py`

```python
#!/usr/bin/env python3
import sys
from datetime import datetime

def parse_jtl(file_path):
    """解析 JMeter JTL 文件"""
    results = []
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith('timeStamp'):
            continue

        parts = line.split(',')
        if len(parts) >= 8:
            try:
                results.append({
                    'elapsed': int(parts[1]),
                    'responseCode': parts[3],
                    'success': parts[7].lower() == 'true'
                })
            except (ValueError, IndexError):
                continue

    return results

def calculate_metrics(results):
    """计算性能指标"""
    elapsed = [r['elapsed'] for r in results if r['success']]
    total = len(results)
    success_count = sum(1 for r in results if r['success'])
    fail_count = total - success_count

    if not elapsed:
        return {
            'total': total,
            'success_count': success_count,
            'fail_count': fail_count,
            'avg': 0,
            'p50': 0,
            'p90': 0,
            'p99': 0,
            'max': 0,
            'min': 0,
            'success_rate': 0
        }

    sorted_elapsed = sorted(elapsed)
    return {
        'total': total,
        'success_count': success_count,
        'fail_count': fail_count,
        'avg': sum(elapsed) / len(elapsed),
        'p50': sorted_elapsed[int(len(sorted_elapsed) * 0.50)],
        'p90': sorted_elapsed[int(len(sorted_elapsed) * 0.90)],
        'p99': sorted_elapsed[int(len(sorted_elapsed) * 0.99)],
        'max': max(sorted_elapsed),
        'min': min(sorted_elapsed),
        'success_rate': (success_count / total * 100) if total > 0 else 0
    }

def main():
    if len(sys.argv) < 3:
        print("Usage: python compare_results.py <baseline.jtl> <current.jtl>")
        sys.exit(1)

    baseline_file = sys.argv[1]
    current_file = sys.argv[2]

    baseline_metrics = calculate_metrics(parse_jtl(baseline_file))
    current_metrics = calculate_metrics(parse_jtl(current_file))

    print("=" * 70)
    print("性能回归验证报告")
    print("=" * 70)
    print(f"基线文件: {baseline_file}")
    print(f"当前文件: {current_file}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print(f"{'指标':<20} {'基线':<12} {'当前':<12} {'变化':<12} {'状态':<10}")
    print("-" * 70)

    for key, label in [
        ('success_rate', '成功率(%)'),
        ('avg', '平均响应(ms)'),
        ('p50', 'P50(ms)'),
        ('p90', 'P90(ms)'),
        ('p99', 'P99(ms)'),
        ('max', '最大响应(ms)')
    ]:
        b = baseline_metrics.get(key, 0)
        c = current_metrics.get(key, 0)

        if key == 'success_rate':
            change = c - b
            status = "✅ PASS" if change >= 0 and c >= 95 else "❌ FAIL"
            print(f"{label:<20} {b:<12.2f} {c:<12.2f} {change:+.2f}%    {status}")
        elif b > 0:
            change = ((c - b) / b * 100)
            status = "✅ PASS" if change < 20 else "❌ FAIL"
            print(f"{label:<20} {b:<12.2f} {c:<12.2f} {change:+.1f}%     {status}")
        else:
            print(f"{label:<20} {b:<12.2f} {c:<12.2f} {'N/A':<12} {'N/A':<10}")

    print("-" * 70)
    print(f"总请求数: 基线={baseline_metrics['total']}, 当前={current_metrics['total']}")
    print(f"成功数:   基线={baseline_metrics['success_count']}, 当前={current_metrics['success_count']}")
    print(f"失败数:   基线={baseline_metrics['fail_count']}, 当前={current_metrics['fail_count']}")

    if current_metrics['success_rate'] < 95:
        print("\n❌ 警告: 成功率低于 95%，需要检查!")
    else:
        print("\n✅ 成功率达标")

if __name__ == '__main__':
    main()