from rich.live import Live
from rich.table import Table
import time
from typing import Callable

from _stats import Metrics

def render(get_metrics: Callable, interval: float = 2) -> None:
    with Live(refresh_per_second=4) as live:
        while True:
            data = get_metrics()
            table = create_table(data)
            
            live.update(table)
            time.sleep(interval)
            
def create_table(data: Metrics) -> Table:
    table = Table(title="System Metrics")
    table.add_column("Metric")
    table.add_column("Value")
    
    cpu = data["cpu"]
    memory = data["memory"]

    table.add_row("CPU Usage", f"{cpu['total_percent']}%")
    table.add_row("CPU Cores", str(cpu["core_count"]))
    for i, core in enumerate(cpu["per_core_percent"]):
        table.add_row(f"CPU Core {i}", f"{core}%")
    
    table.add_row("Memory Used", f"{memory["used"] / 1e9:.2f} GB")
    table.add_row("Memory Percent", f"{memory["percent"]}%")
    
    for disk in data["disks"]:
        table.add_row(
            f"Disk ({disk["device"]})",
            f"{disk["percent"]}%"
        )
        
    return table