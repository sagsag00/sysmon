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
        
    def log(self, metrics) -> None:
        """Appends a single metric snapshot to the log file."""
        success = False
        if self.format == "json":
            self._log_json(metrics)
            success = True
        elif self.format == "csv":
            self._log_csv(metrics)
            success = True
            
        return success
            
    def _log_json(self, metrics):
        timestamp = datetime.now()
        date = timestamp.date().strftime("%Y-%m-%d")
        time = timestamp.time().strftime("%H:%M:%S")
        log_data = {}
        
        if Path(self.path).exists():
            try:
                with open(self.path, "r") as f:
                    log_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError, PermissionError):
                log_data = {}
                
        if date not in log_data:
            log_data[date] = {}
    
        log_data[date][time] = {"metrics": metrics}
    
        try:
            with open(self.path, "w") as f:
                json.dump(log_data, f, indent=4)
        except (PermissionError, FileNotFoundError):
            return
            
    def _log_csv(self, metrics):
        row = {
            "timestamp": datetime.now().isoformat(),
            "cpu_total_percent": metrics["cpu"]["total_percent"],
            "cpu_core_count": metrics["cpu"]["core_count"],
            "memory_used (GiB)": metrics["memory"]["used"],
            "memory_total (GiB)": metrics["memory"]["total"],
            "memory_percent": metrics["memory"]["percent"],
            "download_speed (MB/s)": metrics["network"]["download"],
            "upload_speed (MB/s)": metrics["network"]["upload"]
        }
        for i, disk in enumerate(metrics["disks"]):
            row[f"disk_{i}_mount"] = disk["mountpoint"]
            row[f"disk_{i}_percent"] = disk["percent"]
            row[f"disk_{i}_used (GB)"] = disk["used"]
            row[f"disk_{i}_total (GB)"] = disk["total"]

        write_header = not self.path.exists()
        try:
            with open(self.path, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=row.keys())
                if write_header:
                    writer.writeheader()
                writer.writerow(row)
        except (PermissionError, FileNotFoundError):
            return
            