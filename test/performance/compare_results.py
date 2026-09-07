
---

### 文件 6：`test/performance/compare_results.py`

```python
#!/usr/bin/env python3
import sys
import json
from datetime import datetime

def parse_jtl(file_path):
    results = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('timeStamp'):
            continue
        parts = line.strip().split(',')
        if len(parts) >= 5:
            results.append({
                'elapsed': int(parts[1]),
                'responseCode': parts[3],
                'success': parts[4] == 'true'
            })
    return results

def calculate_metrics(results):
    elapsed = [r['elapsed'] for r in results if r['success']]
    if not elapsed:
        return None
    return {
        'total': len(results),
        'success_count': sum(1 for r in results if r['success']),
        'fail_count': sum(1 for r in results if not r['success']),
        'avg': sum(elapsed) / len(elapsed),
        'p50': sorted(elapsed)[int(len(elapsed) * 0.50)],
        'p90': sorted(elapsed)[int(len(elapsed) * 0.90)],
        'p99': sorted(elapsed)[int(len(elapsed) * 0.99)],
    }

def main():
    if len(sys.argv) < 3:
        print("Usage: python compare_results.py <baseline.jtl> <current.jtl>")
        sys.exit(1)

    baseline = calculate_metrics(parse_jtl(sys.argv[1]))
    current = calculate_metrics(parse_jtl(sys.argv[2]))

    print("=" * 60)
    print("性能回归验证报告")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"| {'指标':<20} | {'基线':<10} | {'当前':<10} | {'变化':<10} |")
    print(f"| {'-'*20} | {'-'*10} | {'-'*10} | {'-'*10} |")
    for key in ['avg', 'p50', 'p90', 'p99']:
        b = baseline[key] if baseline else 0
        c = current[key] if current else 0
        change = ((c - b) / b * 100) if b > 0 else 0
        status = "✅" if change < 20 else "❌"
        print(f"| {key:<20} | {b:<10.2f} | {c:<10.2f} | {change:+.1f}% {status} |")

if __name__ == '__main__':
    main()