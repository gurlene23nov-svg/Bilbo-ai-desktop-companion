import platform
from datetime import datetime

import psutil


def get_cpu_usage():
    return round(psutil.cpu_percent(interval=0.5), 1)


def get_memory_info():
    memory = psutil.virtual_memory()

    return {
        "total_gb": round(memory.total / (1024 ** 3), 2),
        "used_gb": round(memory.used / (1024 ** 3), 2),
        "available_gb": round(memory.available / (1024 ** 3), 2),
        "percent": round(memory.percent, 1),
    }


def get_disk_info(drive):
    try:
        usage = psutil.disk_usage(drive)

        return {
            "drive": drive,
            "total_gb": round(usage.total / (1024 ** 3), 2),
            "used_gb": round(usage.used / (1024 ** 3), 2),
            "free_gb": round(usage.free / (1024 ** 3), 2),
            "percent": round(usage.percent, 1),
        }

    except OSError:
        return None


def get_battery_info():
    battery = psutil.sensors_battery()

    if battery is None:
        return {
            "available": False,
            "percent": None,
            "plugged": None,
        }

    return {
        "available": True,
        "percent": round(battery.percent, 1),
        "plugged": battery.power_plugged,
    }


def get_system_report():
    memory = get_memory_info()
    battery = get_battery_info()

    disks = []

    for drive in ["C:\\", "D:\\"]:
        disk = get_disk_info(drive)

        if disk:
            disks.append(disk)

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_percent": get_cpu_usage(),
        "memory": memory,
        "disks": disks,
        "battery": battery,
    }


def format_system_report(report):
    lines = []

    lines.append("🐰 BILBO'S LAPTOP REPORT")
    lines.append("=" * 30)

    lines.append("")
    lines.append(
        f"💻 System: {report['system']} {report['release']}"
    )

    lines.append(
        f"⚙️ CPU usage: {report['cpu_percent']}%"
    )

    memory = report["memory"]

    lines.append(
        f"🧠 RAM: {memory['percent']}% used "
        f"({memory['used_gb']} GB / {memory['total_gb']} GB)"
    )

    lines.append("")
    lines.append("💾 STORAGE")

    for disk in report["disks"]:
        lines.append(
            f"{disk['drive']} "
            f"{disk['percent']}% used | "
            f"{disk['free_gb']} GB free / "
            f"{disk['total_gb']} GB"
        )

    lines.append("")

    battery = report["battery"]

    if battery["available"]:
        charging = "charging" if battery["plugged"] else "not charging"

        lines.append(
            f"🔋 Battery: {battery['percent']}% ({charging})"
        )
    else:
        lines.append("🔋 Battery: information unavailable")

    lines.append("")
    lines.append("🔐 READ-ONLY CHECK")
    lines.append(
        "Bilbo has only inspected your system. "
        "No files were changed or deleted."
    )

    # Simple warnings
    warnings = []

    for disk in report["disks"]:
        if disk["percent"] >= 95:
            warnings.append(
                f"⚠️ {disk['drive']} drive is critically full."
            )
        elif disk["percent"] >= 85:
            warnings.append(
                f"⚠️ {disk['drive']} drive is getting full."
            )

    if memory["percent"] >= 90:
        warnings.append("⚠️ RAM usage is currently very high.")

    if report["cpu_percent"] >= 90:
        warnings.append("⚠️ CPU usage is currently very high.")

    if warnings:
        lines.append("")
        lines.append("⚠️ BILBO'S NOTES")

        for warning in warnings:
            lines.append(warning)

    else:
        lines.append("")
        lines.append(
            "💚 Bilbo says: Your laptop looks okay right now!"
        )

    return "\n".join(lines)