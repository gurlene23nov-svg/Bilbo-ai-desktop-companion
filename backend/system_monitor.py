import psutil
import time


def get_cpu_usage():
    return psutil.cpu_percent(interval=0.3)


def get_memory_usage():

    memory = psutil.virtual_memory()

    return {
        "percent": memory.percent,
        "used_gb": round(
            memory.used / (1024 ** 3),
            2
        ),
        "total_gb": round(
            memory.total / (1024 ** 3),
            2
        ),
    }


def get_disk_usage():

    disk = psutil.disk_usage("C:\\")

    return {
        "percent": disk.percent,
        "used_gb": round(
            disk.used / (1024 ** 3),
            2
        ),
        "free_gb": round(
            disk.free / (1024 ** 3),
            2
        ),
        "total_gb": round(
            disk.total / (1024 ** 3),
            2
        ),
    }


def get_battery():

    battery = psutil.sensors_battery()

    if battery is None:
        return {
            "available": False
        }

    return {
        "available": True,
        "percent": battery.percent,
        "plugged": battery.power_plugged,
    }


def get_uptime():

    boot_time = psutil.boot_time()

    uptime_seconds = time.time() - boot_time

    hours = int(uptime_seconds // 3600)
    minutes = int(
        (uptime_seconds % 3600) // 60
    )

    return {
        "hours": hours,
        "minutes": minutes,
    }


def get_system_status():

    return {
        "cpu": get_cpu_usage(),
        "memory": get_memory_usage(),
        "disk": get_disk_usage(),
        "battery": get_battery(),
        "uptime": get_uptime(),
    }