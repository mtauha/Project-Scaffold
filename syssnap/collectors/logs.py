import subprocess


def collect():
    logs = {}
    try:
        # dmesg log
        dmesg = subprocess.run(
            ["dmesg", "--time-format=iso"], capture_output=True, text=True
        )
        logs["dmesg"] = dmesg.stdout[-4096:]  # Limit to last 4KB

        # Last 100 boot log lines via journalctl
        try:
            journal = subprocess.run(
                ["journalctl", "-b", "-n", "100"], capture_output=True, text=True
            )
            logs["journalctl_boot"] = journal.stdout
        except Exception:
            logs["journalctl_boot"] = "journalctl not available"
    except Exception as e:
        logs["error"] = str(e)
    return logs
