import json
import csv
from pathlib import Path
from collections import defaultdict

from src.report import get_by_date, _search_csv, _search_json, to_date_str, to_time_str, _update_stats

def create_log_file(path, format=None):
    data = {
        "2026-03-16": {
            "10:54:32": {
                "metrics": {
                    "cpu": {
                        "total_percent": 80
                    },
                    "disks": [
                        {
                            "device": "C:\\",
                            "mountpoint": "C:\\",
                            "total": 100
                        }
                    ]
                }
            },
            "10:54:33": {
                "metrics": {
                    "cpu": {
                        "total_percent": 100
                    }
                }
            }
        }
    }
    row = {
        "timestamp": "2026-03-16T10:54:32",
        "cpu_total_percent": 80.1,
    }
    if not format:
        format = Path(path).suffix.replace(".", "")
    
    with open(path, "w") as f:
        if format == "json":
            json.dump(data, f)
        elif format == "csv":
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writeheader()
            writer.writerow(row)

def test_get_by_date(tmp_path):
    assert get_by_date(None, None) == {}
    
    date = "2026-03-16"
    
    assert get_by_date(tmp_path, date) == {}
    
    log_file = tmp_path / "log.txt"
    assert get_by_date(log_file, date) == {}
    
    log_file = tmp_path / "log.json"
    create_log_file(log_file)
    assert get_by_date(log_file, date) != {}
    
    log_file = tmp_path / "log.csv"
    create_log_file(log_file)
    assert get_by_date(log_file, date) != {}
    
def test_to_date_str():
    date = "2026-03-16"
    assert to_date_str(date) == date
    
    date_hour = "2026-03-16T10:54:03"
    assert to_date_str(date_hour) == date
    
def test_to_time_str():
    time = "10:54:03"
    assert to_time_str(time) == time
    
    date_hour = "2026-03-16T10:54:03"
    assert to_time_str(date_hour) == time
    
def test_search_json(tmp_path):
    assert _search_json(None, None) == {}
    
    date = "2026-03-16"
    other_date = "2026-03-17"
    log_file = tmp_path / "log.json"

    assert _search_json(tmp_path, date) == {}
    assert _search_json(log_file, date) == {}
    
    create_log_file(log_file)
    assert _search_json(log_file, other_date) == {}
    
    result = _search_json(log_file, date) 
    assert result["avg"]["cpu.total_percent"] == 90.0
    assert result["max"]["cpu.total_percent"][0] == 100
    assert result["min"]["cpu.total_percent"][0] == 80
    assert result["avg"].get("disks.C:\\.mountpoint") == None
    assert result["avg"]["disks.C:\\.total"] == 100
    
    
def test_search_csv(tmp_path):
    assert _search_csv(None, None) == {}
    
    date = "2026-03-16"
    other_date = "2026-03-17"
    timestamp = "2026-03-16T10:54:03"
    log_file = tmp_path / "log.csv"
    stats = {'avg': {'cpu_total_percent': 80.1}, 'max': {'cpu_total_percent': (80.1, '10:54:32')}, 'min': {'cpu_total_percent': (80.1, '10:54:32')}}
    
    assert _search_csv(tmp_path, date) == {}
    assert _search_csv(log_file, date) == {}
    
    create_log_file(log_file)
    assert _search_csv(log_file, date) == _search_csv(log_file, timestamp)
    assert _search_csv(log_file, other_date) == {}
    assert _search_csv(log_file, date) == stats

def test_update_stats():
    stats = defaultdict(lambda: {"sum": 0, "count": 0})
    stats_copy = stats.copy()
    max_dict, min_dict = {}, {}
    
    assert _update_stats("test", "fake", "time", max_dict, min_dict, stats) == {}
    assert stats == stats_copy
    assert _update_stats("test", 1, "time", max_dict, min_dict, stats) == None
    assert stats == {'test': {'sum': 1, 'count': 1}}