import subprocess
import shutil


def collect():
    svcs = {}
    try:
        if shutil.which("systemctl"):
            list_units = subprocess.run(
                ["systemctl", "list-units", "--type=service", "--state=running,failed"],
                capture_output=True,
                text=True,
            )
            svcs["systemctl"] = list_units.stdout
        elif shutil.which("service"):
            service_list = subprocess.run(
                ["service", "--status-all"], capture_output=True, text=True
            )
            svcs["service"] = service_list.stdout
        else:
            svcs["error"] = "No known service manager found"
    except Exception as e:
        svcs["error"] = str(e)
    return svcs
