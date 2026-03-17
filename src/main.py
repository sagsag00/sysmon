import threading
import argparse
import sys

from collector import collect_metrics
from display import render, print_data, print_error
from logger import Logger
from report import get_by_date
from config import Config

def parse_args():
    """Parses the given commandline args"""
    parser = argparse.ArgumentParser(description="SysMon - System Monitoring CLI Tool")
    parser.add_argument(
        "--interval", "-i",
        type=float,
        default=2.0,
        help="Polling interval in seconds (default: 2s)"
    )
    parser.add_argument(
        "--log", "-l",
        type=str,
        default=None,
        help="Path to log file (CSV or JSON)"
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["json", "csv"],
        default="json",
        help="Log file extension"
    )
    parser.add_argument(
        "--date", "-d",
        type=str,
        default=None,
        help="Prints max/min/avg of each metric for the given date"
    )
    parser.add_argument(
        "--cpu-warn", 
        type=float,
        default=85,
        help="Sets a cpu threshold that when exceeded a warning notification will be sent"
    )
    parser.add_argument(
        "--mem-warn",
        type=float,
        default=85,
        help="Sets a memory threshold that when exceeded a warning notification will be sent"
    )
    
    return parser.parse_args()

def create_logger(log_path: str):
    logger = Logger(log_path) 
    
    logging_thread = threading.Thread(
        target=logger.start_logging,
        args=(collect_metrics,),
        daemon=True)
    logging_thread.start()

def render_display():
    try:
        render(collect_metrics)
    except KeyboardInterrupt:
        print_error("\nSysMon stopped by user.")
        sys.exit(0)
        
def print_daily_report(date: str, log_path: str):
    if not date:
        return
    
    data = get_by_date(log_path, date)
    if data:
        print_data(data, date)
    else:
        print_error(f"Couldn't retrieve data from log file: {log_path}")

def main():
    args = parse_args()
    
    config = Config.get_instance()
    config.cpu_warn =  args.cpu_warn
    config.mem_warn = args.mem_warn
    config.interval = args.interval
    
    log_path = args.log or f"logs/log.{args.format}"
    
    print_daily_report(args.date, log_path)
    
    create_logger(log_path)
    
    render_display()
    
if __name__ == "__main__":
    main()
        