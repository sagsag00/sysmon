import psutil

# from _stats import CPUStats, MemoryStats, DiskStats, NetworkStats, Metrics

def collect_metrics(interval: float = 2):
    """
    Collect all system metrics.

    Returns:
        dict: Contains the following metrics:
            cpu (dict): CPU usage statistics:
                - total_percent (float)
                - per_core_percent (list[float])
                - core_count (int | None)

            memory (dict): Memory statistics:
                - total (int)
                - used (int)
                - available (int)
                - percent (float)

            disks (list[dict]): Disk statistics for each partition:
                - device (str)
                - mountpoint (str)
                - total (int)
                - used (int)
                - free (int)
                - percent (float)
            
            network (dict): Network statistics:
                - download (int)
                - upload (int)
    """
    return {
        "cpu": get_cpu(interval),
        "memory": get_memory(),
        "disks": get_disks(),
        "network": get_network()
    }

def get_cpu(interval: float = 2):
    """
    Collect CPU usage statistics.
    
    Args:
        int: The interval between checks in seconds. Default: 2.

    Returns:
        dict: CPU statistics containing:
            total_percent (float): Overall CPU usage percentage.
            per_core_percent (list[float]): CPU usage percentage per core.
            core_count (int | None): Number of CPU cores.
    """
    per_core = psutil.cpu_percent(interval=interval, percpu=True)
    total = round(sum(per_core) / len(per_core), 1)
    return {
        "total_percent": total,
        "per_core_percent": per_core,
        "core_count": psutil.cpu_count()
    }

def get_memory():
    """
    Get memory statistics.

    Returns:
        dict: Memory statistics containing:
            total (int): The total memory in the system.
            used (int): The amount of used memory.
            available (int): The amount of free/available memory.
            percent (float): Percent usage. 
    """
    memory = psutil.virtual_memory()
    
    return {
        "total": memory.total,
        "used": memory.used,
        "available": memory.available,
        "percent": memory.percent
    }

def get_disks():
    """
    Get statistics for each disk partition.

    Returns:
        list[dict]: Statistics for each partition containing:
            device (str): Device path.
            mountpoint (str): Mountpoint path.
            total (int): Total bytes in the disk.
            used (int): Used bytes.
            free (int): Free bytes.
            percent (float): Percent usage.
    """
    disks = []
    
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (PermissionError, FileNotFoundError):
            continue
        
        disks.append({
            "device": part.device,
            "mountpoint": part.mountpoint,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent
        })
        
    return disks

def get_network():
    """Gets the download and upload speeds"""
    net = psutil.net_io_counters()

    return {
        "download": net.bytes_recv,
        "upload": net.bytes_sent
    }