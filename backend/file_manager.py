from pathlib import Path
import os
import shutil
import tempfile

# ============================================================
# PROTECTED LOCATIONS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

PROTECTED_PATHS = [
    PROJECT_DIR,
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path.home() / "Pictures",
]


# ============================================================
# COMMON TEMP LOCATIONS
# ============================================================

def get_temp_locations():
    locations = []

    temp_dir = Path(tempfile.gettempdir())

    if not is_protected(temp_dir) and temp_dir.exists():
        locations.append(temp_dir)

    temp_value = os.environ.get("TEMP")

    if temp_value:
        windows_temp = Path(temp_value)

        if (
            not is_protected(windows_temp)
            and windows_temp.exists()
            and windows_temp not in locations
        ):
            locations.append(windows_temp)

    return locations


# ============================================================
# SIZE FORMATTER
# ============================================================

def format_size(size_bytes):
    size = float(size_bytes)

    units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB"
    ]

    for unit in units:
        if size < 1024:
            return f"{size:.1f} {unit}"

        size /= 1024

    return f"{size:.1f} PB"


# ============================================================
# CHECK PROTECTED PATH
# ============================================================

def is_protected(path):
    try:
        path = Path(os.path.abspath(Path(path)))

        for candidate in (path, *path.parents):
            if candidate.name.casefold() == "gurlene":
                return True

            if candidate.is_symlink() or candidate.is_junction():
                return True

        path = path.resolve()
    except (OSError, RuntimeError, ValueError):
        return True

    if any(part.casefold() == "gurlene" for part in path.parts):
        return True

    for protected in PROTECTED_PATHS:

        try:
            protected = protected.resolve()

            if path == protected:
                return True

            if protected in path.parents:
                return True

        except Exception:
            continue

    return False


# ============================================================
# STORAGE SUMMARY
# ============================================================

def get_storage_summary(drive="C:\\"):

    try:

        usage = shutil.disk_usage(drive)

        total = usage.total
        used = usage.used
        free = usage.free

        used_percent = (used / total) * 100

        return {
            "drive": drive,
            "total": format_size(total),
            "used": format_size(used),
            "free": format_size(free),
            "used_percent": round(used_percent, 1),
        }

    except OSError as error:

        return {
            "error": str(error)
        }


# ============================================================
# FIND LARGE FILES
# ============================================================

def find_large_files(
    folder=None,
    minimum_mb=500,
    max_results=20
):

    if folder is None:
        folder = Path.home() / "Downloads"

    folder = Path(folder)

    if is_protected(folder):
        return []

    if not folder.exists():
        return []

    minimum_bytes = minimum_mb * 1024 * 1024

    results = []

    try:

        for root, dirs, files in os.walk(folder):

            # Avoid protected directories.
            dirs[:] = [
                d for d in dirs
                if not is_protected(Path(root) / d)
            ]

            for filename in files:

                path = Path(root) / filename

                try:

                    if is_protected(path):
                        continue

                    size = path.stat().st_size

                    if size >= minimum_bytes:

                        results.append({
                            "name": path.name,
                            "path": str(path),
                            "size": format_size(size),
                            "size_bytes": size,
                        })

                except (OSError, PermissionError):
                    continue

    except (OSError, PermissionError):
        pass

    results.sort(
        key=lambda item: item["size_bytes"],
        reverse=True
    )

    return results[:max_results]


# ============================================================
# FIND TEMP FILES
# ============================================================

def find_temp_files(max_results=30):

    results = []

    for folder in get_temp_locations():

        if is_protected(folder):
            continue

        if not folder.exists():
            continue

        try:

            for path in folder.iterdir():

                try:

                    if not path.exists():
                        continue

                    if is_protected(path):
                        continue

                    if path.is_file():

                        size = path.stat().st_size

                        results.append({
                            "name": path.name,
                            "path": str(path),
                            "size": format_size(size),
                            "size_bytes": size,
                            "category": "temporary",
                        })

                except (
                    OSError,
                    PermissionError
                ):
                    continue

        except (
            OSError,
            PermissionError
        ):
            continue

    results.sort(
        key=lambda item: item["size_bytes"],
        reverse=True
    )

    return results[:max_results]


# ============================================================
# STORAGE SCAN
# ============================================================

def scan_storage():

    downloads = Path.home() / "Downloads"

    large_files = find_large_files(
        downloads,
        minimum_mb=500,
        max_results=15
    )

    temp_files = find_temp_files(
        max_results=15
    )

    large_bytes = sum(
        item["size_bytes"]
        for item in large_files
    )

    temp_bytes = sum(
        item["size_bytes"]
        for item in temp_files
    )

    return {
        "storage": get_storage_summary(),
        "large_downloads": large_files,
        "temporary_files": temp_files,
        "large_downloads_total": format_size(large_bytes),
        "temporary_files_total": format_size(temp_bytes),
    }


# ============================================================
# SECURITY CHECK
# ============================================================

def get_security_report():

    report = {
        "windows_defender": "Unknown",
        "firewall": "Unknown",
        "notes": [],
    }

    # --------------------------------------------------------
    # Windows Defender
    # --------------------------------------------------------

    try:

        import subprocess

        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                "Get-MpComputerStatus | "
                "Select-Object AntivirusEnabled,"
                "RealTimeProtectionEnabled,"
                "AntivirusSignatureLastUpdated | "
                "ConvertTo-Json"
            )
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout.strip():

            report["windows_defender"] = (
                result.stdout.strip()
            )

    except Exception as error:

        report["notes"].append(
            f"Could not check Defender: {error}"
        )


    # --------------------------------------------------------
    # Windows Firewall
    # --------------------------------------------------------

    try:

        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                "Get-NetFirewallProfile | "
                "Select-Object Name,Enabled | "
                "ConvertTo-Json"
            )
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout.strip():

            report["firewall"] = (
                result.stdout.strip()
            )

    except Exception as error:

        report["notes"].append(
            f"Could not check Firewall: {error}"
        )


    return report