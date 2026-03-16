from rich.live import Live
from rich.console import Console
from rich.table import Table
import time
from typing import Callable

from _stats import Metrics
from config import Config

def render(get_metrics: Callable, args: tuple = None) -> None:
    """Renders a table of metrics that auto updates every 1 seconds."""
    with Live(refresh_per_second=4) as live:
        while True:
            data = get_metrics(*(args or ()))
            table = create_table(data)
            
            live.update(table)
            time.sleep(1)
            
def print_data(data: dict) -> None:
    """Prints given data in a readable format"""
    console = Console()
    console.print(create_report_table(data))
            
def create_report_table(data: dict) -> Table:
    """Creates a table displaying min, max, and avg stats from a report"""
    table = Table(title="System Metrics Report")
    table.add_column("Metric")
    table.add_column("Min")
    table.add_column("Max")
    table.add_column("Avg")

    def fmt_percent(key, val, time):
        return f"{val:.1f}% @ {time}"

    def fmt_val(val, time, unit=""):
        return f"{val:.2f}{unit} @ {time}"

    def fmt_avg(val, unit=""):
        return f"{val:.2f}{unit}"

    max_d, min_d, avg_d = data["max"], data["min"], data["avg"]

    table.add_row(
        "CPU Usage",
        fmt_percent("cpu.total_percent", min_d["cpu.total_percent"][0], min_d["cpu.total_percent"][1]),
        fmt_percent("cpu.total_percent", max_d["cpu.total_percent"][0], max_d["cpu.total_percent"][1]),
        fmt_avg(avg_d["cpu.total_percent"], "%")
    )
    table.add_row(
        "CPU Cores",
        str(min_d["cpu.core_count"][0]),
        str(max_d["cpu.core_count"][0]),
        str(int(avg_d["cpu.core_count"]))
    )

    table.add_section()

    table.add_row(
        "Memory Usage",
        fmt_val(min_d["memory.used"][0], min_d["memory.used"][1], " GiB"),
        fmt_val(max_d["memory.used"][0], max_d["memory.used"][1], " GiB"),
        fmt_avg(avg_d["memory.used"], " GiB")
    )
    table.add_row(
        "Memory Percent",
        fmt_percent("memory.percent", min_d["memory.percent"][0], min_d["memory.percent"][1]),
        fmt_percent("memory.percent", max_d["memory.percent"][0], max_d["memory.percent"][1]),
        fmt_avg(avg_d["memory.percent"], "%")
    )

    table.add_section()

    disk_keys = {
        k.split(".")[1]
        for k in max_d
        if k.startswith("disks.")
    }
    for device in sorted(disk_keys):
        percent_key = f"disks.{device}.percent"
        used_key = f"disks.{device}.used"
        total_key = f"disks.{device}.total"
        table.add_row(
            f"Disk {device}",
            fmt_percent(percent_key, min_d[percent_key][0], min_d[percent_key][1]),
            fmt_percent(percent_key, max_d[percent_key][0], max_d[percent_key][1]),
            f"{fmt_avg(avg_d[used_key], ' GB')} / {avg_d[total_key]:.2f} GB"
        )

    table.add_section()

    table.add_row(
        "Download",
        fmt_val(min_d["network.download"][0], min_d["network.download"][1], " MB"),
        fmt_val(max_d["network.download"][0], max_d["network.download"][1], " MB"),
        fmt_avg(avg_d["network.download"], " MB")
    )
    table.add_row(
        "Upload",
        fmt_val(min_d["network.upload"][0], min_d["network.upload"][1], " MB"),
        fmt_val(max_d["network.upload"][0], max_d["network.upload"][1], " MB"),
        fmt_avg(avg_d["network.upload"], " MB")
    )

    return table
            
def create_table(data: Metrics) -> Table:
    """Creates a table with the provided data"""
    table = Table(title="System Metrics")
    table.add_column("Metric")
    table.add_column("Value")
    
    cpu = data["cpu"]
    memory = data["memory"]

    table.add_row("CPU Usage", f"[{format_color(cpu['total_percent'], "cpu")}]{cpu['total_percent']}%")
    table.add_row("CPU Cores", str(cpu["core_count"]))
    for i, core in enumerate(cpu["per_core_percent"]):
        table.add_row(f"CPU Core {i}", f"[{format_color(core, "cpu")}]{core}%")
        
    table.add_section()
    
    table.add_row("Memory Usage ", f"[{format_color(memory['percent'], "memory")}]{memory['used']} GiB / {memory['total']} GiB")
    table.add_row("Memory Percent", f"[{format_color(memory['percent'], "memory")}]{memory['percent']}%")
    
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

def format_color(percent: float, component: str = "") -> str:
    """
    Returns `green` if percent < 0.7 * threshold.
    `yellow` if 0.7 * threshold <= percent < threshold.
    `red` if percent >= threshold.
    """
    threshold = 85
    if component == "cpu":
        threshold = Config.cpu_warn
    elif component == "memory":
        threshold = Config.mem_warn
    
    if percent < 0.7 * threshold:
        return "green"
    if percent < threshold:
        return "yellow"
    return "red"