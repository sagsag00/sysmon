from rich.live import Live
from rich.table import Table
import time
from typing import Callable

from _stats import Metrics

def render(get_metrics: Callable, interval: float = 1) -> None:
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

    table.add_row("CPU Usage", f"[{format_color(cpu['total_percent'])}]{cpu['total_percent']}%")
    table.add_row("CPU Cores", str(cpu["core_count"]))
    for i, core in enumerate(cpu["per_core_percent"]):
        table.add_row(f"CPU Core {i}", f"[{format_color(core)}]{core}%")
        
    table.add_section()
    
    table.add_row("Memory Usage ", f"[{format_color(memory['percent'])}]{memory['used'] / 1e9:.2f} GB / {memory['total'] / 1e9:.2f} GB")
    table.add_row("Memory Percent", f"[{format_color(memory['percent'])}]{memory['percent']}%")
    
    table.add_section()
    
    for disk in data["disks"]:
        table.add_row(
            f"Disk {disk['mountpoint']}",
            f"[{format_color(disk['percent'])}]{disk['percent']:.1f}% ({disk['used'] / 1e9:.2f} GB / {disk['total'] / 1e9:.2f} GB)"
        )
        
    return table

def format_color(percent: float) -> str:
    if percent < 60:
        return "green"
    if percent < 85:
        return "yellow"
    return "red"