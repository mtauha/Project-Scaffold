import subprocess


def collect():
    cpu_info = {}
    try:
        lscpu = subprocess.run(["lscpu"], capture_output=True, text=True)
        for line in lscpu.stdout.splitlines():
            if ":" in line:
                key, val = [s.strip() for s in line.split(":", 1)]
                cpu_info[key] = val
        with open("/proc/cpuinfo") as f:
            for line in f:
                if ":" in line:
                    key, val = [s.strip() for s in line.split(":", 1)]
                    cpu_info.setdefault(key, []).append(val)
    except Exception as e:
        cpu_info["error"] = str(e)
    return cpu_info
