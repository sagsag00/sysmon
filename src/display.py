from rich.live import Live
from rich.table import Table
import time
from typing import Callable

from _stats import Metrics

def render(get_metrics: Callable, args: tuple = None) -> None:
    """Renders a table of metrics that auto updates every 1 seconds."""
    with Live(refresh_per_second=4) as live:
        while True:
            data = get_metrics(*(args or ()))
            table = create_table(data)
            
            live.update(table)
            time.sleep(1)
            
def create_table(data: Metrics) -> Table:
    """Creates a table with the provided data"""
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
    
    table.add_row("Memory Usage ", f"[{format_color(memory['percent'])}]{memory['used']} GiB / {memory['total']} GiB")
    table.add_row("Memory Percent", f"[{format_color(memory['percent'])}]{memory['percent']}%")
    
    table.add_section()
    
    for disk in data["disks"]:
        table.add_row(
            f"Disk {disk['mountpoint']}",
            f"[{format_color(disk['percent'])}]{disk['percent']:.1f}% ({disk['used']} GB / {disk['total']} GB)"
        )
        
    table.add_section()
    
    network = data["network"]
    
    table.add_row("Download Speed", f"[blue]{network['download']} MB/s")
    table.add_row("Upload Speed", f"[blue]{network['upload']} MB/s")
        
    return table

def format_color(percent: float) -> str:
    """
    Returns `green` if percent < 60.
    `yellow` if 60 <= percent < 85.
    `red` if percent >= 85.
    

    Args:
        percent (float): _description_

    Returns:
        str: _description_
    """
    if percent < 60:
        return "green"
    if percent < 85:
        return "yellow"
    return "red"