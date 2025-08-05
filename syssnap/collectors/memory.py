def collect():
    meminfo = {}
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if ":" in line:
                    key, val = [s.strip() for s in line.split(":", 1)]
                    meminfo[key] = val
    except Exception as e:
        meminfo["error"] = str(e)
    return meminfo
