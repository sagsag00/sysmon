import json
import csv

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
        ]
    }
    
def test_json_logging(tmp_path):
    log_file = tmp_path / "metrics.json"
    
    logger = Logger(str(log_file))
    logger.log(fake_metrics())
    
    assert log_file.exists()
    
    with open(log_file) as f:
        line = f.readline()
        data = json.loads(line)
    
    assert "timestamp" in data
    assert data["metrics"]["cpu"]["total_percent"] == 50
    
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