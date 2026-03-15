from typing import TypedDict

class CPUStats(TypedDict):
    total_percent: float
    per_core_percent: list[float]
    core_count: int | None
    
class MemoryStats(TypedDict):
    total: int
    used: int
    available: int
    percent: float
    
class DiskStats(TypedDict):
    device: str
    mountpoint: str
    total: int
    used: int
    free: int
    percent: float
    
class Metrics(TypedDict):
    cpu: CPUStats
    memory: MemoryStats
    disk: list[DiskStats]