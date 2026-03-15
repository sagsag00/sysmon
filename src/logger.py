import json
import csv
from pathlib import Path
from typing import Callable
import time

from src._stats import Metrics

class Logger:
    def __init__(self, path: str, format: str = "json"):
        self.path = Path(path)
        self.format = format.lower()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
    def start_logging(self, get_metrics: Callable, interval: float = 1):
        """Starts logging until proram stops."""
        while True:
            metrics = get_metrics()
            self.log(metrics)
            time.sleep(interval)
        
    def log(self, metrics: Metrics):
        """Appends a single metric snapshot to the log file."""
        
        if self.format == "json":
            self._log_json(metrics)
        elif self.format == "csv":
            self._log_csv(metrics)
            
    def _log_json(self, metrics: Metrics):
        with open(self.path, "a") as f:
            f.write(json.dumps(metrics) + "\n")
            
    def _log_csv(self, metrics: Metrics):
        row = {
            "cpu_total_percent": metrics["cpu"]["total_percent"],
            "cpu_core_count": metrics["cpu"]["core_count"],
            "memory_used": metrics["memory"]["used"],
            "memory_total": metrics["memory"]["total"],
            "memory_percent": metrics["memory"]["percent"]
        }
        for i, disk in enumerate(metrics["disks"]):
            row[f"disk_{i}_mount"] = disk["mountpoint"]
            row[f"disk_{i}_percent"] = disk["percent"]
            row[f"disk_{i}_used"] = disk["used"]
            row[f"disk_{i}_total"] = disk["total"]

        write_header = not self.path.exists()
        with open(self.path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(row)
            