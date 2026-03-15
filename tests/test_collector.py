from unittest.mock import patch

from src.collector import get_cpu, get_memory, get_disks, collect_metrics
from src._stats import CPUStats, MemoryStats, DiskStats, Metrics

def test_get_cpu():
    with patch("psutil.cpu_percent") as mock_cpu, patch("psutil.cpu_count") as mock_count:
        mock_cpu.side_effect = [25, [10, 20, 30, 40]]
        mock_count.return_value = 4
        
        cpu: CPUStats = get_cpu()
        assert cpu["total_percent"] == 25
        assert cpu["per_core_percent"] == [10, 20, 30, 40]
        assert cpu["core_count"] == 4
        
def test_get_memory():
    mock_memory = type("vmem", (), {})()
    mock_memory.total = 4000
    mock_memory.used = 400
    mock_memory.available = 3600
    mock_memory.percent = 10
    
    with patch("psutil.virtual_memory", return_value=mock_memory):
        memory: MemoryStats = get_memory()
        assert memory["total"] == 4000
        assert memory["used"] == 400
        assert memory["available"] == 3600
        assert memory["percent"] == 10
        
def test_get_disks():
    mock_partition = type("Partition", (), {})()
    mock_partition.device = "/dev/sda1"
    mock_partition.mountpoint = "/"
    
    mock_usage = type("Usage", (), {})()
    mock_usage.total = 1000
    mock_usage.used = 100
    mock_usage.free = 900
    mock_usage.percent = 10
    
    with patch("psutil.disk_partitions", return_value=[mock_partition]):
        with patch("psutil.disk_usage", return_value=mock_usage):
            disks: list[DiskStats] = get_disks()
            assert len(disks) == 1
            assert disks[0]["device"] == "/dev/sda1"
            assert disks[0]["mountpoint"] == "/"
            assert disks[0]["total"] == 1000
            assert disks[0]["used"] == 100
            assert disks[0]["free"] == 900
            assert disks[0]["percent"] == 10
            
def test_collect_metrics():
    with patch("src.collector.get_cpu") as mock_cpu, patch("src.collector.get_memory") as mock_memory, patch("src.collector.get_disks") as mock_disks:
        mock_cpu.return_value = {"total_percent": 10, "per_core_percent": [10, 10], "core_count": 2}
        mock_memory.return_value = {"total": 4000, "used": 400, "available": 3600, "percent": 10}
        mock_disks.return_value = [{"device": "/dev/sda1", "mountpoint": "/", "total": 1000, "used": 100, "free": 900, "percent": 10}]
        
        metrics = collect_metrics()
        assert "cpu" in metrics
        assert "memory" in metrics
        assert "disks" in metrics