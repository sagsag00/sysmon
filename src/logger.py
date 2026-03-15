import json
import csv
from pathlib import Path
from typing import Callable
import time
from datetime import datetime

# from _stats import Metrics

class Logger:
    def __init__(self, path: str):
        self.path = Path(path)
        self.format = self.path.suffix.replace(".", "")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
    def start_logging(self, get_metrics: Callable, args: tuple):
        """Starts logging until program stops."""
        while True:
            metrics = get_metrics(*(args or ()))
            self.log(metrics)
            time.sleep(1)
        
    def log(self, metrics):
        """Appends a single metric snapshot to the log file."""
        if self.format == "json":
            self._log_json(metrics)
        elif self.format == "csv":
            self._log_csv(metrics)
            
    def _log_json(self, metrics):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        try:
            with open(self.path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except (PermissionError, FileNotFoundError):
            return
            
    def _log_csv(self, metrics):
        row = {
            "timestamp": datetime.now().isoformat(),
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
        try:
            with open(self.path, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=row.keys())
                if write_header:
                    writer.writeheader()
                writer.writerow(row)
        except (PermissionError, FileNotFoundError):
            return
            