import os
from pathlib import Path

import psutil


# ============================================================
# MEMORY INFORMATION
# ============================================================

def get_memory_info():
    memory = psutil.virtual_memory()

    return {
        "total_gb": round(memory.total / (1024 ** 3), 2),
        "used_gb": round(memory.used / (1024 ** 3), 2),
        "available_gb": round(memory.available / (1024 ** 3), 2),
        "percent": memory.percent,
    }


# ============================================================
# TOP MEMORY-USING PROCESSES
# ============================================================

def get_top_memory_processes(limit=10):
    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "memory_info", "memory_percent"]
    ):
        try:
            info = process.info
            memory_info = info.get("memory_info")

            if memory_info is None:
                continue

            memory_mb = memory_info.rss / (1024 ** 2)

            processes.append({
                "pid": info.get("pid"),
                "name": info.get("name") or "Unknown",
                "memory_mb": round(memory_mb, 1),
                "memory_percent": round(
                    info.get("memory_percent") or 0,
                    1
                ),
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    processes.sort(
        key=lambda item: item["memory_mb"],
        reverse=True
    )

    return processes[:limit]


# ============================================================
# TOP CPU-USING PROCESSES
# ============================================================

def get_top_cpu_processes(limit=10):
    processes = []

    # Initialize CPU counters.
    for process in psutil.process_iter(["pid", "name"]):
        try:
            process.cpu_percent(interval=None)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    # Measure CPU for a short interval.
    psutil.cpu_percent(interval=0.5)

    for process in psutil.process_iter(["pid", "name"]):
        try:
            cpu = process.cpu_percent(interval=None)

            processes.append({
                "pid": process.info.get("pid"),
                "name": process.info.get("name") or "Unknown",
                "cpu_percent": round(cpu, 1),
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    processes.sort(
        key=lambda item: item["cpu_percent"],
        reverse=True
    )

    return processes[:limit]


# ============================================================
# SAFE DIRECTORY SIZE
# ============================================================

def get_directory_size(path, max_files=30000):
    """
    Read-only directory size calculation.

    This function NEVER:
        - deletes files
        - moves files
        - renames files
        - changes files
    """

    total_size = 0
    scanned_files = 0

    ignored_directories = {
        "$Recycle.Bin",
        "System Volume Information",
        "Recovery",
        "WindowsApps",
    }

    try:

        for root, dirs, files in os.walk(path):

            # Avoid known protected/system directories.
            dirs[:] = [
                directory
                for directory in dirs
                if directory not in ignored_directories
            ]

            for filename in files:

                if scanned_files >= max_files:
                    return total_size

                file_path = os.path.join(
                    root,
                    filename
                )

                try:
                    total_size += os.path.getsize(
                        file_path
                    )

                    scanned_files += 1

                except (
                    PermissionError,
                    FileNotFoundError,
                    OSError,
                ):
                    continue

    except (
        PermissionError,
        FileNotFoundError,
        OSError,
    ):
        pass

    return total_size


# ============================================================
# USER FOLDER STORAGE
# ============================================================

def get_user_storage():
    home = Path.home()

    folders = {
        "Desktop": home / "Desktop",
        "Documents": home / "Documents",
        "Downloads": home / "Downloads",
        "Pictures": home / "Pictures",
        "Videos": home / "Videos",
    }

    results = []

    for name, path in folders.items():

        if not path.exists():
            continue

        size = get_directory_size(
            str(path),
            max_files=30000
        )

        results.append({
            "name": name,
            "path": str(path),
            "size_gb": round(
                size / (1024 ** 3),
                2
            ),
        })

    results.sort(
        key=lambda item: item["size_gb"],
        reverse=True
    )

    return results


# ============================================================
# FIND LARGE FILES
# ============================================================

def find_large_files(
    directory=None,
    minimum_mb=500,
    max_files_scanned=50000,
    limit=10,
):
    """
    Finds large files without modifying anything.
    """

    if directory is None:
        directory = str(Path.home())

    minimum_bytes = minimum_mb * 1024 * 1024

    large_files = []
    scanned_files = 0

    ignored_directories = {
        "$Recycle.Bin",
        "System Volume Information",
        "Recovery",
        "WindowsApps",
    }

    try:

        for root, dirs, files in os.walk(directory):

            dirs[:] = [
                directory_name
                for directory_name in dirs
                if directory_name not in ignored_directories
            ]

            for filename in files:

                if scanned_files >= max_files_scanned:
                    break

                file_path = os.path.join(
                    root,
                    filename
                )

                try:

                    size = os.path.getsize(
                        file_path
                    )

                    scanned_files += 1

                    if size >= minimum_bytes:

                        large_files.append({
                            "name": filename,
                            "path": file_path,
                            "size_gb": round(
                                size / (1024 ** 3),
                                2
                            ),
                        })

                except (
                    PermissionError,
                    FileNotFoundError,
                    OSError,
                ):
                    continue

            if scanned_files >= max_files_scanned:
                break

    except (
        PermissionError,
        FileNotFoundError,
        OSError,
    ):
        pass

    large_files.sort(
        key=lambda item: item["size_gb"],
        reverse=True
    )

    return large_files[:limit]


# ============================================================
# STORAGE REPORT
# ============================================================

def get_storage_report():

    report = {
        "drives": [],
        "user_folders": [],
        "large_files": [],
    }

    # --------------------------------------------------------
    # Drives
    # --------------------------------------------------------

    for partition in psutil.disk_partitions():

        drive = partition.mountpoint

        try:

            usage = psutil.disk_usage(drive)

            report["drives"].append({
                "drive": drive,
                "total_gb": round(
                    usage.total / (1024 ** 3),
                    2
                ),
                "used_gb": round(
                    usage.used / (1024 ** 3),
                    2
                ),
                "free_gb": round(
                    usage.free / (1024 ** 3),
                    2
                ),
                "percent": usage.percent,
            })

        except (
            PermissionError,
            FileNotFoundError,
            OSError,
        ):
            continue

    # --------------------------------------------------------
    # Personal folders
    # --------------------------------------------------------

    report["user_folders"] = get_user_storage()

    # --------------------------------------------------------
    # Large files
    # --------------------------------------------------------

    report["large_files"] = find_large_files(
        directory=str(Path.home()),
        minimum_mb=500,
        max_files_scanned=50000,
        limit=10,
    )

    return report


# ============================================================
# MEMORY REPORT
# ============================================================

def format_memory_report():

    memory = get_memory_info()
    processes = get_top_memory_processes()

    lines = []

    lines.append("🧠 BILBO'S MEMORY DETECTIVE")
    lines.append("=" * 31)
    lines.append("")

    lines.append(
        f"RAM usage: {memory['percent']}%"
    )

    lines.append(
        f"Used: {memory['used_gb']} GB / "
        f"{memory['total_gb']} GB"
    )

    lines.append(
        f"Available: {memory['available_gb']} GB"
    )

    lines.append("")
    lines.append("🔥 TOP MEMORY USERS")
    lines.append("")

    if processes:

        for index, process in enumerate(
            processes,
            start=1
        ):

            lines.append(
                f"{index}. {process['name']} — "
                f"{process['memory_mb']} MB"
            )

    else:

        lines.append(
            "No process information available."
        )

    lines.append("")

    if memory["percent"] >= 90:

        lines.append(
            "🔴 Bilbo's note: RAM usage is VERY HIGH."
        )

    elif memory["percent"] >= 75:

        lines.append(
            "🟠 Bilbo's note: RAM usage is getting high."
        )

    else:

        lines.append(
            "🟢 Bilbo's note: RAM usage looks okay."
        )

    lines.append("")
    lines.append("🔐 READ-ONLY")
    lines.append(
        "Bilbo only inspected running processes."
    )
    lines.append(
        "No processes were stopped."
    )

    return "\n".join(lines)


# ============================================================
# STORAGE REPORT
# ============================================================

def format_storage_report():

    report = get_storage_report()

    lines = []

    lines.append("🐰 BILBO'S STORAGE DETECTIVE")
    lines.append("=" * 33)
    lines.append("")

    # --------------------------------------------------------
    # Drives
    # --------------------------------------------------------

    lines.append("💾 DRIVES")
    lines.append("")

    if report["drives"]:

        for drive in report["drives"]:

            lines.append(
                f"{drive['drive']} "
                f"{drive['percent']}% used | "
                f"{drive['free_gb']} GB free / "
                f"{drive['total_gb']} GB"
            )

    else:

        lines.append(
            "No drive information available."
        )

    # --------------------------------------------------------
    # Personal folders
    # --------------------------------------------------------

    lines.append("")
    lines.append("📁 YOUR LARGEST FOLDERS")
    lines.append("")

    if report["user_folders"]:

        for index, folder in enumerate(
            report["user_folders"],
            start=1
        ):

            lines.append(
                f"{index}. {folder['name']} — "
                f"{folder['size_gb']} GB"
            )

    else:

        lines.append(
            "No personal folders could be analyzed."
        )

    # --------------------------------------------------------
    # Large files
    # --------------------------------------------------------

    lines.append("")
    lines.append("🔎 LARGE FILES")
    lines.append("")

    if report["large_files"]:

        for index, file in enumerate(
            report["large_files"],
            start=1
        ):

            lines.append(
                f"{index}. {file['name']} — "
                f"{file['size_gb']} GB"
            )

            lines.append(
                f"   {file['path']}"
            )

    else:

        lines.append(
            "No large files found in the scanned area."
        )

    # --------------------------------------------------------
    # Safety
    # --------------------------------------------------------

    lines.append("")
    lines.append("🔐 READ-ONLY")
    lines.append(
        "Bilbo only inspected your storage."
    )
    lines.append(
        "No files were changed, moved, or deleted."
    )

    return "\n".join(lines)