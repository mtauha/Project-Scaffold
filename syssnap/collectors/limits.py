import subprocess
import os


def collect():
    limits = {}
    try:
        # Get current shell limits with ulimit -a
        ulimit = subprocess.run(["ulimit", "-a"], capture_output=True, text=True, shell=True)
        limits["ulimit"] = ulimit.stdout
        
        # Parse ulimit output for structured data
        ulimit_structured = {}
        for line in ulimit.stdout.strip().split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().replace('(', '').replace(')', '')
                    value = parts[1].strip()
                    ulimit_structured[key] = value
        limits["ulimit_structured"] = ulimit_structured
        
        # System-wide limits from /proc/sys/kernel/
        kernel_limits = {}
        kernel_limit_files = [
            "pid_max",
            "threads-max", 
            "max_user_instances",
            "max_user_watches",
            "nr_open",
            "file-max"
        ]
        
        for limit_file in kernel_limit_files:
            try:
                with open(f"/proc/sys/kernel/{limit_file}") as f:
                    kernel_limits[limit_file] = f.read().strip()
            except Exception:
                kernel_limits[limit_file] = "N/A"
        
        limits["kernel_limits"] = kernel_limits
        
        # File system limits from /proc/sys/fs/
        fs_limits = {}
        fs_limit_files = [
            "file-nr",
            "file-max", 
            "inode-nr",
            "inode-state",
            "dentry-state"
        ]
        
        for limit_file in fs_limit_files:
            try:
                with open(f"/proc/sys/fs/{limit_file}") as f:
                    fs_limits[limit_file] = f.read().strip()
            except Exception:
                fs_limits[limit_file] = "N/A"
                
        limits["fs_limits"] = fs_limits
        
        # User limits configuration
        try:
            if os.path.exists("/etc/security/limits.conf"):
                with open("/etc/security/limits.conf") as f:
                    # Filter out comments and empty lines
                    config_lines = []
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            config_lines.append(line)
                    limits["limits_conf"] = config_lines
        except Exception:
            limits["limits_conf"] = "N/A"
            
        # Additional limits.d directory
        try:
            limits_d_path = "/etc/security/limits.d/"
            if os.path.exists(limits_d_path):
                limits_d_files = {}
                for filename in os.listdir(limits_d_path):
                    if filename.endswith('.conf'):
                        try:
                            with open(os.path.join(limits_d_path, filename)) as f:
                                config_lines = []
                                for line in f:
                                    line = line.strip()
                                    if line and not line.startswith('#'):
                                        config_lines.append(line)
                                limits_d_files[filename] = config_lines
                        except Exception:
                            continue
                limits["limits_d"] = limits_d_files
        except Exception:
            limits["limits_d"] = "N/A"
            
        # Container limits detection
        container_limits = {}
        
        # Check for Docker container
        if os.path.exists("/.dockerenv"):
            container_limits["container_type"] = "docker"
            
            # Docker memory limits
            try:
                with open("/sys/fs/cgroup/memory/memory.limit_in_bytes") as f:
                    container_limits["memory_limit"] = f.read().strip()
            except Exception:
                try:
                    # cgroup v2
                    with open("/sys/fs/cgroup/memory.max") as f:
                        container_limits["memory_limit"] = f.read().strip()
                except Exception:
                    container_limits["memory_limit"] = "N/A"
                    
            # Docker CPU limits
            try:
                with open("/sys/fs/cgroup/cpu/cpu.cfs_quota_us") as f:
                    quota = f.read().strip()
                with open("/sys/fs/cgroup/cpu/cpu.cfs_period_us") as f:
                    period = f.read().strip()
                container_limits["cpu_quota"] = quota
                container_limits["cpu_period"] = period
            except Exception:
                try:
                    # cgroup v2
                    with open("/sys/fs/cgroup/cpu.max") as f:
                        container_limits["cpu_max"] = f.read().strip()
                except Exception:
                    container_limits["cpu_max"] = "N/A"
                    
        # Check for LXC container
        elif os.path.exists("/proc/1/environ"):
            try:
                with open("/proc/1/environ", 'rb') as f:
                    environ = f.read().decode('utf-8', errors='ignore')
                    if 'container=lxc' in environ:
                        container_limits["container_type"] = "lxc"
            except Exception:
                pass
                
        if container_limits:
            limits["container_limits"] = container_limits
            
        # Current resource usage for context
        try:
            with open("/proc/loadavg") as f:
                limits["current_load"] = f.read().strip()
        except Exception:
            limits["current_load"] = "N/A"
            
    except Exception as e:
        limits["error"] = str(e)
    
    return limits