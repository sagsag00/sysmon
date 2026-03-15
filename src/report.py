import json
import csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def to_date_str(date_str: str) -> str:
    """
    Convert a date string or full ISO timestamp to `YYYY-MM-DD`.
    """
    if "." in date_str or "T" in date_str:
        dt = datetime.fromisoformat(date_str)
        return dt.date().strftime("%Y-%m-%d")
    else:
        return date_str
    
def print_by_date(log_path: str, date: str):
    log_file = Path(log_path)
    if not log_file.exists():
        print("File not found")
        return
    
    if "json" in log_file.suffix:
        _search_json(log_file, date)
    elif "csv" in log_file.suffix:
        _search_csv(log_file, date)
        
def _search_json(file: Path, date: str) -> dict:
    with open(file) as f:
        data: dict = json.load(f)
        
    if date not in data:
        return None
        
    current_data: dict = data[date]
    max_dict, min_dict = {}, {}
    stats: dict[str, list] = defaultdict(lambda: {"sum": 0, "count": 0})
    
    for time, metrics in current_data.items():
        for metric_category, sub_metrics in metrics.items():
            for metric_name, value in sub_metrics.items():
                key = f"{metric_category}.{metric_name}"
                
                if key not in max_dict or value > max_dict[key][0]:
                    max_dict[key] = (value, time)
                if key not in min_dict or value < min_dict[key][0]:
                    min_dict[key] = (value, time)

                stats[key]["sum"] += value
                stats[key]["count"] += 1
                
    avg_dict = {k: s["sum"] / s["count"] for k, s in stats.items()}
    
    return {
        "max": max_dict,
        "min": min_dict,
        "avg": avg_dict
    }
    
def _search_csv(file: Path, date: str) -> dict:
    pass