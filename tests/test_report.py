import json
import csv
from pathlib import Path
from collections import defaultdict

import pytest

from src.report import (
    get_by_date,
    _search,
    _extract_csv,
    _extract_disks,
    _extract_json,
    _extract_regular,
    to_date_str,
    to_time_str,
    _update_stats,
)

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
    assert get_by_date(tmp_path, None) == {}

    date = "2026-03-16"
    
    # non-existing file
    log_file = tmp_path / "log.txt"
    assert get_by_date(log_file, date) == {}

    # JSON log
    log_file = tmp_path / "log.json"
    create_log_file(log_file)
    result = get_by_date(log_file, date)
    assert result != {}
    assert result["avg"]["cpu.total_percent"] == 90.0
    assert result["max"]["cpu.total_percent"][0] == 100
    assert result["min"]["cpu.total_percent"][0] == 80
    assert result["avg"].get("disks.C:\\.mountpoint") is None
    assert result["avg"]["disks.C:\\.total"] == 100
    
    # CSV log
    log_file = tmp_path / "log.csv"
    create_log_file(log_file)
    result_csv = get_by_date(log_file, date)
    assert result_csv != {}
    assert result_csv["avg"]["cpu.total_percent"] == pytest.approx(80.1)
    assert result_csv["max"]["cpu.total_percent"][0] == 80.1
    assert result_csv["min"]["cpu.total_percent"][0] == 80.1
    
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
    date = "2026-03-16"
    other_date = "2026-03-17"
    log_file = tmp_path / "log.json"

    # empty or invalid input
    assert _search(log_file, other_date, _extract_json) == {}
    
    create_log_file(log_file)
    result = _search(log_file, date, _extract_json)
    assert result["avg"]["cpu.total_percent"] == 90.0
    assert result["max"]["cpu.total_percent"][0] == 100
    assert result["min"]["cpu.total_percent"][0] == 80
    assert result["avg"].get("disks.C:\\.mountpoint") is None
    assert result["avg"]["disks.C:\\.total"] == 100
    
    
def test_search_csv(tmp_path):
    date = "2026-03-16"
    other_date = "2026-03-17"
    log_file = tmp_path / "log.csv"

    create_log_file(log_file)
    result = _search(log_file, date, _extract_csv)
    
    # Stats checks
    assert result["avg"]["cpu.total_percent"] == pytest.approx(80.1)
    assert result["max"]["cpu.total_percent"][0] == 80.1
    assert result["min"]["cpu.total_percent"][0] == 80.1

    # Searching for a non-existent date
    assert _search(log_file, other_date, _extract_csv) == {'avg': {}, 'max': {}, 'min': {}}

def test_update_stats():
    stats = defaultdict(lambda: {"sum": 0, "count": 0})
    stats_copy = stats.copy()
    max_dict, min_dict = {}, {}

    # Non-numeric value is ignored
    _update_stats("test", "fake", "time", max_dict, min_dict, stats)
    assert stats == stats_copy
    assert max_dict == {}
    assert min_dict == {}

    # Numeric value is processed correctly
    _update_stats("test", 1, "time", max_dict, min_dict, stats)
    assert stats == {"test": {"sum": 1, "count": 1}}
    assert max_dict["test"][0] == 1
    assert min_dict["test"][0] == 1