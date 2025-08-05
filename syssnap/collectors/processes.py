import subprocess


def collect():
    procs = {}
    try:
        # Running processes (ps aux)
        ps = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        procs["ps_aux"] = ps.stdout

        # Top 10 by memory
        top = subprocess.run(
            ["ps", "-eo", "pid,ppid,user,cmd,%mem,%cpu", "--sort=-%mem"],
            capture_output=True,
            text=True,
        )
        procs["top_by_mem"] = "\n".join(top.stdout.splitlines()[:12])
    except Exception as e:
        procs["error"] = str(e)
    return procs
