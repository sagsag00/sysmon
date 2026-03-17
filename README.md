# System Metrics Monitor

A Python tool for collecting, logging, and reporting system metrics (CPU, memory, disk, network) using `psutil` and `rich`.

![Alt text](assets/live.png)
![Alt text](assets/report.png)

## Features

- Real-time live display of system metrics in the terminal
- Logging to JSON or CSV formats
- Report generation with min/max/avg stats from log files
- Configurable warning thresholds for CPU and memory

## Installation
```bash
pip install psutil rich
```

## Usage

```
python src/main.py [--log LOG_FILE] [--format FORMAT] [--interval INTERVAL] [--cpu-warn CPU_WARN] [--mem-warn MEM_WARN] [--date DATE]
```

| Argument | Required | Default | Description |
|---|---|---|---|
| `--log` | No | — | Path to the log file |
| `--format` | No | `json` | Log format: `json` or `csv`. ignored if `--log` is provided|
| `--interval` | No | `2` | Seconds between metric collections |
| `--cpu-warn` | No | `85` | CPU usage % at which the display turns red |
| `--mem-warn` | No | `85` | Memory usage % at which the display turns red |
| `--date` | No | — | If provided, show a report for this date (`YYYY-MM-DD`) before the live display |

## Examples

Start live monitoring, logging to CSV:
```base
python src/main.py --format csv
```

Log to a custom JSON path with a custom interval and warning thresholds:
```base
python src/main.py --log metrics.json --interval 5 --cpu-warn 75 --mem-warn 80
```

Show a report for a specific date:
```base
python src/main.py --date 2026-03-16
```

## Log Formats

### JSON

```json
{"timestamp": "2026-03-17T15:23:13.084731",
    "metrics": 
    {"cpu": 
        {"total_percent": 0.0, "per_core_percent": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "core_count": 6},
    "memory": 
        {"total": 31.94, "used": 17.59, "available": 14.34, "percent": 55.1},
    "disks": 
        [{"device": "C:\\", "mountpoint": "C:\\", "total": 498.26, "used": 430.66, "free": 67.6, "percent": 86.4},
         {"device": "D:\\", "mountpoint": "D:\\", "total": 500.1, "used": 424.19, "free": 75.92, "percent": 84.8}], 
    "network": 
        {"download": 14815.73, "upload": 437.49}
    }
}
```

### CSV

Each row is a timestamped snapshot with flattened columns:

```
timestamp,cpu_total_percent,cpu_core_count,memory_used (GiB),...,disk_0_mount,disk_0_percent,...
2026-03-16T10:00:00,45.2,8,6.1,...,/,60.0,...
```

## Running Tests

```bash
pytest tests/
```