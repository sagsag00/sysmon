import threading
import argparse
import sys
from rich import print

from collector import collect_metrics
from display import render, print_data
from logger import Logger
from report import get_by_date

def parse_args():
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
    
    return parser.parse_args()

def main():
    args = parse_args()
    interval = args.interval
    log_path = args.log
    log_format = args.format
    date = args.date
    
    log_path = log_path if log_path else f"logs/log.{log_format}"
    
    if date:
        data = get_by_date(log_path, date)
        print_data(data)
    
    logger = Logger(log_path) 
    
    if logger:
        logging_thread = threading.Thread(target=logger.start_logging, args=(collect_metrics, (interval,)), daemon=True)
        logging_thread.start()
    
    try:
        render(collect_metrics, args=(interval,))
    except KeyboardInterrupt:
        print("\n[bold red]SysMon stopped by user.[/bold red]")
        sys.exit(0)
    
if __name__ == "__main__":
    main()
        