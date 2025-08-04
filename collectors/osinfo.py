import platform
import subprocess


def collect():
    os_info = {}
    try:
        os_info["platform"] = platform.platform()
        os_info["system"] = platform.system()
        os_info["release"] = platform.release()
        os_info["version"] = platform.version()
        os_info["architecture"] = platform.machine()
        os_info["hostname"] = platform.node()
        # Distro info
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        os_info[k] = v.strip('"')
        except Exception:
            os_info["os-release"] = "N/A"

        uptime = subprocess.run(["uptime", "-p"], capture_output=True, text=True)
        os_info["uptime"] = uptime.stdout.strip()

    except Exception as e:
        os_info["error"] = str(e)
    return os_info
