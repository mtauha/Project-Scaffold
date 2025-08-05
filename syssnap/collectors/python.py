import sys
import subprocess


def collect():
    py = {}
    try:
        py["sys_version"] = sys.version
        py["sys_executable"] = sys.executable
        # Installed pip packages
        pip = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format", "freeze"],
            capture_output=True,
            text=True,
        )
        py["pip"] = pip.stdout
        # Virtualenv/conda?
        py["VIRTUAL_ENV"] = sys.prefix
    except Exception as e:
        py["error"] = str(e)
    return py
