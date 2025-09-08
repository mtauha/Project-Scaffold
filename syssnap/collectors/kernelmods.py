import subprocess
import shutil


def collect():
    kernelmods = {}
    try:
        # Get loaded kernel modules with lsmod
        lsmod = subprocess.run(["lsmod"], capture_output=True, text=True)
        kernelmods["lsmod"] = lsmod.stdout
        
        # Parse lsmod output for structured data
        modules = []
        lines = lsmod.stdout.strip().split('\n')[1:]  # Skip header
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                module_data = {
                    "name": parts[0],
                    "size": int(parts[1]) if parts[1].isdigit() else parts[1],
                    "used_by_count": int(parts[2]) if parts[2].isdigit() else 0,
                    "dependencies": parts[3].split(',') if len(parts) > 3 and parts[3] != '-' else []
                }
                modules.append(module_data)
        kernelmods["modules_structured"] = modules
        
        # Get detailed info for critical/commonly problematic modules
        critical_modules = ["nvidia", "amdgpu", "i915", "nouveau", "radeon", "iwlwifi", "ath9k", "rtw88", "r8169", "e1000e"]
        module_details = {}
        
        for module in critical_modules:
            # Check if module is loaded
            if any(m["name"] == module for m in modules):
                try:
                    modinfo = subprocess.run(["modinfo", module], capture_output=True, text=True)
                    if modinfo.returncode == 0:
                        module_details[module] = modinfo.stdout
                except Exception:
                    continue
        
        kernelmods["critical_module_details"] = module_details
        
        # Get kernel version
        try:
            uname = subprocess.run(["uname", "-r"], capture_output=True, text=True)
            kernelmods["kernel_version"] = uname.stdout.strip()
        except Exception:
            kernelmods["kernel_version"] = "N/A"
            
        # Get module loading configuration
        try:
            if shutil.which("find"):
                # Look for module configuration files
                modconf = subprocess.run(
                    ["find", "/etc/modprobe.d/", "-name", "*.conf", "-type", "f"],
                    capture_output=True, text=True
                )
                if modconf.returncode == 0:
                    kernelmods["modprobe_configs"] = modconf.stdout.strip().split('\n')
        except Exception:
            pass
            
    except Exception as e:
        kernelmods["error"] = str(e)
    
    return kernelmods