import subprocess
import shutil


def collect():
    pkgs = {}
    try:
        # Try dpkg (Debian/Ubuntu)
        if shutil.which("dpkg"):
            dpkg = subprocess.run(["dpkg", "-l"], capture_output=True, text=True)
            pkgs["dpkg"] = dpkg.stdout
        # Try rpm (RHEL/Fedora)
        elif shutil.which("rpm"):
            rpm = subprocess.run(["rpm", "-qa"], capture_output=True, text=True)
            pkgs["rpm"] = rpm.stdout
        # Try pacman (Arch)
        elif shutil.which("pacman"):
            pacman = subprocess.run(["pacman", "-Q"], capture_output=True, text=True)
            pkgs["pacman"] = pacman.stdout
        else:
            pkgs["error"] = "No known package manager found"
    except Exception as e:
        pkgs["error"] = str(e)
    return pkgs
