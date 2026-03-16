import json
import csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def get_by_date(log_path: str, date: str) -> dict:
    """Gets a report by date from the provided log file (path)"""
    if not log_path or not date:
        return {}
    
    log_file = Path(log_path)
    if not log_file.exists():
        return {}
    
    data = {}
    if "json" in log_file.suffix:
        data = _search_json(log_file, date)
    elif "csv" in log_file.suffix:
        data = _search_csv(log_file, to_date_str(date))
        
    return data 

def to_date_str(date_str: str) -> str:
    """
    Convert a date string or full ISO timestamp to `YYYY-MM-DD`.
    """
    if "." in date_str or "T" in date_str:
        dt = datetime.fromisoformat(date_str)
        return dt.date().strftime("%Y-%m-%d")
    else:
        return date_str
    
def to_time_str(date_str: str) -> str:
    """
    Convert a date string or full ISO timestamp to `HH:MM:SS`
    """
    if "." in date_str or "T" in date_str:
        dt = datetime.fromisoformat(date_str)
        return dt.time().strftime("%H:%M:%S")
    else:
        return date_str
        
def _search_json(file: Path, date: str) -> dict:
    if not file or not file.exists():
        return {}
    
    try:
        with open(file) as f:
            data: dict = json.load(f)
    except (PermissionError, FileNotFoundError):
        return {}
        
    if date not in data:
        return {}
        
    current_data: dict = data[date]
    max_dict, min_dict = {}, {}
    stats: dict[str, list] = defaultdict(lambda: {"sum": 0, "count": 0})
    
    for time, metrics in current_data.items():
        metrics = metrics["metrics"]
        for metric_category, sub_metrics in metrics.items():
            if metric_category == "disks":
                for disk in sub_metrics:
                    device = disk["device"].replace("/dev/", "")
                    for metric_name, value in disk.items():
                        if metric_name in ("device", "mountpoint"):
                            continue
                        key = f"disks.{device}.{metric_name}"
                        _update_stats(key, value, time, max_dict, min_dict, stats)
            else:
                for metric_name, value in sub_metrics.items():
                    if metric_name in ("core_count"):
                        continue
                    key = f"{metric_category}.{metric_name}"
                    _update_stats(key, value, time, max_dict, min_dict, stats)
                    
    avg_dict = {k: s["sum"] / s["count"] for k, s in stats.items()}
    
    return {
        "max": max_dict,
        "min": min_dict,
        "avg": avg_dict
    }
    
def _search_csv(file: Path, date: str) -> dict:
    if not file or not file.exists():
        return {}
    
    try:
        with open(file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except (PermissionError, FileNotFoundError):
        return {}
        
    if not rows:
        return {}
    
    current_data = [
        row for row in rows
        if to_date_str(row["timestamp"]) == to_date_str(date)
    ]
    
    if not current_data:
        return {}
    
    max_dict, min_dict = {}, {}
    stats: dict[str, list] = defaultdict(lambda: {"sum": 0, "count": 0})
    
    for row in current_data:
        time = to_time_str(row["timestamp"])
        for key, value in row.items():
            if key == "timestamp":
                continue
            
            _update_stats(key, float(value), time, max_dict, min_dict, stats)

    avg_dict = {k: s["sum"] / s["count"] for k, s in stats.items()}
    
    return {
        "max": max_dict,
        "min": min_dict,
        "avg": avg_dict
    }
    
def _update_stats(key: str, value: int | float, time: str, max_dict: dict, min_dict: dict, stats: defaultdict):
    if not isinstance(value, (int, float)):
        return {}
    
    if key not in max_dict or value > max_dict[key][0]:
        max_dict[key] = (value, time)
    if key not in min_dict or value < min_dict[key][0]:
        min_dict[key] = (value, time)

    stats[key]["sum"] += value
    stats[key]["count"] += 1