import subprocess


def collect():
    net_info = {}
    try:
        # IP addresses and interfaces
        ip = subprocess.run(["ip", "a"], capture_output=True, text=True)
        net_info["ip"] = ip.stdout

        # Routing table
        route = subprocess.run(["ip", "route"], capture_output=True, text=True)
        net_info["route"] = route.stdout

        # DNS resolvers
        try:
            with open("/etc/resolv.conf") as f:
                net_info["resolv.conf"] = f.read()
        except Exception:
            net_info["resolv.conf"] = "N/A"

        # Active connections
        ss = subprocess.run(["ss", "-tulnp"], capture_output=True, text=True)
        net_info["active_connections"] = ss.stdout

    except Exception as e:
        net_info["error"] = str(e)
    return net_info
