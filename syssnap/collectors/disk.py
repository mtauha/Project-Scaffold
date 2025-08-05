import subprocess


def collect():
    disk_info = {"partitions": [], "usage": []}
    try:
        # List block devices
        lsblk = subprocess.run(
            ["lsblk", "-o", "NAME,SIZE,TYPE,MOUNTPOINT"], capture_output=True, text=True
        )
        disk_info["lsblk"] = lsblk.stdout

        # Partition usage
        df = subprocess.run(["df", "-h"], capture_output=True, text=True)
        disk_info["df"] = df.stdout

        # IO statistics
        try:
            iostat = subprocess.run(["iostat"], capture_output=True, text=True)
            disk_info["iostat"] = iostat.stdout
        except Exception:
            disk_info["iostat"] = "iostat not available"

    except Exception as e:
        disk_info["error"] = str(e)
    return disk_info
