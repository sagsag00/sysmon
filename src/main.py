import threading

from collector import collect_metrics
from display import render
from logger import Logger

def main():
    interval = 1
    
    logger = Logger("logs/sysmon.json", format="json")
    logging_thread = threading.Thread(target=logger.start_logging, args=(collect_metrics, interval), daemon=True)
    logging_thread.start()
    
    render(collect_metrics, interval)
    
if __name__ == "__main__":
    main()
        