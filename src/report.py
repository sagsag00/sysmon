import json
import csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Callable, Generator

def get_by_date(log_path: str, date: str) -> dict:
    """Gets a report by date from the provided log file (path)"""
    if not log_path or not date:
        return {}
    
    log_file = Path(log_path)
    if not log_file.exists():
        return {}
    
    data = {}
    if "json" in log_file.suffix:
        data = _search(log_file, date, _extract_json)
    elif "csv" in log_file.suffix:
        data = _search(log_file, date, _extract_csv)
        
    if not any(data.values()):
        return {}
        
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
   
def _search(file: Path, date: str, extractor: Callable[[Path, str], Generator]) -> dict:
    if not file or not file.exists():
        return {}
    
    try:
        data_points: Generator = extractor(file, date)
    except (PermissionError, FileNotFoundError):
        return {}
    
    if not data_points:
        return {}
    
    max_dict, min_dict = {}, {}
    stats = defaultdict(lambda: {"sum": 0, "count": 0})
    
    for time, key, value in data_points:
        _update_stats(key, value, time, max_dict, min_dict, stats)
        
    avg_dict = {k: s["sum"] / s["count"] for k, s in stats.items()}
    
    return {
        "max": max_dict,
        "min": min_dict,
        "avg": avg_dict
    }
        
def _extract_json(file: Path, date: str):
    with open(file) as f:
        data: dict = json.load(f)
        
    current_data: dict[str, dict] = data.get(date)
    if not current_data:
        return []
    
    for time, metrics in current_data.items():
        metrics: dict[str, dict] = metrics["metrics"]
        
        for category, sub_metrics in metrics.items():
            if category == "disks":
                yield from _extract_disks(time, sub_metrics)
                continue
            yield from _extract_regular(time, category, sub_metrics)
                    
def _extract_disks(time: str, disks: list):
    for disk in disks:
        device = disk["device"].replace("/dev/", "")
        for name, value in disk.items():
            if name in ("device", "mountpoint"):
                continue
            if isinstance(value, (int, float)):
                yield time, f"disks.{device}.{name}", value
                
def _extract_regular(time: str, category: str, sub_metrics: dict):
    for name, value in sub_metrics.items():
        if name == "core_count":
            continue
        if isinstance(value, (int, float)):
            yield time, f"{category}.{name}", value
                
def _extract_csv(file: Path, date: str):
    with open(file) as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if to_date_str(row["timestamp"]) != to_date_str(date):
                continue
            
            time = to_time_str(row["timestamp"])
            
            for key, value in row.items():
                if key == "timestamp":
                    continue
                
                try:
                    num = float(value)
                except (TypeError, ValueError):
                    continue
                
                parts = key.split(" ")[0].split("_", 1)
                yield time, f"{parts[0]}.{parts[1]}", num
    
def _update_stats(key: str, value: int | float, time: str, max_dict: dict, min_dict: dict, stats: defaultdict):
    if not isinstance(value, (int, float)):
        return {}
    
    if key not in max_dict or value > max_dict[key][0]:
        max_dict[key] = (value, time)
    if key not in min_dict or value < min_dict[key][0]:
        min_dict[key] = (value, time)

    stats[key]["sum"] += value
    stats[key]["count"] += 1