import json
import csv
from datetime import datetime
from unittest.mock import patch
import pytest
import time

from src.logger import Logger

def fake_metrics():
    return {
        "cpu": {"total_percent": 50, "core_count": 8},
        "memory": {"used": 4000, "total": 8000, "percent": 50},
        "disks": [
            {
                "mountpoint": "/",
                "percent": 60,
                "used": 300,
                "total": 500
            }
        ],
        "network": {
            "download": 1000,
            "upload": 100
        }
    }
    
def test_start_logging(tmp_path):
    log_file = tmp_path / "metrics.json"
    logger = Logger(str(log_file))
    
    call_count = 0
    def fake_get_metrics():
        nonlocal call_count
        call_count += 1
        if call_count >= 3:
            raise StopIteration
        return fake_metrics()
    
    with patch("time.sleep"), patch("src.logger.datetime") as mock_dt:
        mock_dt.now.side_effect = [
            datetime(2026, 3, 16, 10, 0, 0),
            datetime(2026, 3, 16, 10, 0, 1)
        ]
        mock_dt.now.return_value.date.return_value.strftime.return_value = "2026-03-16"
        with pytest.raises(StopIteration):
            logger.start_logging(fake_get_metrics, ())
            
    assert call_count == 3
    
    with open(log_file) as f:
        data = json.load(f)
    
    date = str(datetime.now().date())
    assert len(data[date]) == 2
    
def test_log(tmp_path):
    log_file = tmp_path / "metrics.txt"
    
    logger = Logger(str(log_file))
    assert logger.log(fake_metrics()) == False
    
    del logger
    log_file = tmp_path / "metrics.json"
    logger = Logger(str(log_file))
    assert logger.log(fake_metrics()) == True
    
    del logger
    log_file = tmp_path / "metrics.csv"
    logger = Logger(str(log_file))
    assert logger.log(fake_metrics()) == True

def test_json_logging(tmp_path):
    log_file = tmp_path / "metrics.json"
    
    logger = Logger(str(log_file))
    logger.log(fake_metrics())
    
    assert log_file.exists()
    
    with open(log_file) as f:
        data: dict = json.load(f)
    
    date = str(datetime.now().date())
    
    assert date in data
    
    time_entry = next(iter(data[date].values()))
    assert time_entry["metrics"]["cpu"]["total_percent"] == 50
    
    time.sleep(1)
    
    logger.log(fake_metrics())
    with open(log_file) as f:
        data: dict = json.load(f)
        
    assert len(data[date].values()) == 2
    
def test_csv_logging(tmp_path):
    log_file = tmp_path / "metrics.csv"
    
    logger = Logger(str(log_file))
    logger.log(fake_metrics())
    
    assert log_file.exists()
    
    with open(log_file) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) == 1
    assert int(rows[0]["cpu_total_percent"]) == 50
    
    logger.log(fake_metrics())
    with open(log_file) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 2