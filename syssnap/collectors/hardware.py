import subprocess
import shutil


def collect():
    hw = {}
    try:
        if shutil.which("lshw"):
            lshw = subprocess.run(["lshw", "-short"], capture_output=True, text=True)
            hw["lshw"] = lshw.stdout
        if shutil.which("lsusb"):
            lsusb = subprocess.run(["lsusb"], capture_output=True, text=True)
            hw["lsusb"] = lsusb.stdout
        if shutil.which("lspci"):
            lspci = subprocess.run(["lspci"], capture_output=True, text=True)
            hw["lspci"] = lspci.stdout
        if shutil.which("dmidecode"):
            dmi = subprocess.run(
                ["dmidecode", "-t", "system"], capture_output=True, text=True
            )
            hw["dmidecode_system"] = dmi.stdout
    except Exception as e:
        hw["error"] = str(e)
    return hw
