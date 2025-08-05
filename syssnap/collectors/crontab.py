import subprocess


def collect():
    cron = {}
    try:
        # Per-user crontab
        user_cron = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        cron["user_crontab"] = user_cron.stdout
        # System crontab
        try:
            with open("/etc/crontab") as f:
                cron["etc_crontab"] = f.read()
        except Exception:
            cron["etc_crontab"] = "N/A"
    except Exception as e:
        cron["error"] = str(e)
    return cron
