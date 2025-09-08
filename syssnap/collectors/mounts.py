import subprocess
import os


def collect():
    mounts = {}
    try:
        # Get current mounts using the mount command
        mount_cmd = subprocess.run(["mount"], capture_output=True, text=True)
        if mount_cmd.returncode == 0:
            mounts["mount_command"] = mount_cmd.stdout
        
        # Parse /proc/mounts for detailed mount information
        try:
            with open("/proc/mounts") as f:
                proc_mounts = f.read()
                mounts["proc_mounts"] = proc_mounts
                
                # Parse into structured format
                structured_mounts = []
                for line in proc_mounts.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 6:
                            mount_info = {
                                "device": parts[0],
                                "mountpoint": parts[1], 
                                "filesystem": parts[2],
                                "options": parts[3].split(','),
                                "dump": parts[4],
                                "pass": parts[5]
                            }
                            structured_mounts.append(mount_info)
                mounts["mounts_structured"] = structured_mounts
                
        except Exception as e:
            mounts["proc_mounts_error"] = str(e)
        
        # Get /etc/fstab for persistent mount configuration
        try:
            if os.path.exists("/etc/fstab"):
                with open("/etc/fstab") as f:
                    fstab_content = f.read()
                    mounts["fstab"] = fstab_content
                    
                    # Parse fstab into structured format
                    fstab_entries = []
                    for line in fstab_content.strip().split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split()
                            if len(parts) >= 6:
                                fstab_entry = {
                                    "device": parts[0],
                                    "mountpoint": parts[1],
                                    "filesystem": parts[2], 
                                    "options": parts[3].split(','),
                                    "dump": parts[4],
                                    "pass": parts[5]
                                }
                                fstab_entries.append(fstab_entry)
                    mounts["fstab_structured"] = fstab_entries
        except Exception as e:
            mounts["fstab_error"] = str(e)
        
        # Categorize filesystems for easier analysis
        if "mounts_structured" in mounts:
            categories = {
                "physical": [],
                "virtual": [],
                "network": [],
                "special": [],
                "readonly": [],
                "issues": []
            }
            
            virtual_fs = ["proc", "sysfs", "devfs", "tmpfs", "devpts", "cgroup", "cgroup2", "securityfs", "debugfs"]
            network_fs = ["nfs", "nfs4", "cifs", "smb", "sshfs", "fuse.sshfs"]
            
            for mount in mounts["mounts_structured"]:
                fs_type = mount["filesystem"]
                options = mount["options"]
                
                # Categorize by filesystem type
                if fs_type in virtual_fs:
                    categories["virtual"].append(mount)
                elif fs_type in network_fs:
                    categories["network"].append(mount)
                elif fs_type in ["ext2", "ext3", "ext4", "xfs", "btrfs", "ntfs", "vfat", "exfat"]:
                    categories["physical"].append(mount)
                else:
                    categories["special"].append(mount)
                
                # Check for read-only mounts
                if "ro" in options:
                    categories["readonly"].append(mount)
                
                # Identify potential issues
                issues = []
                if "ro" in options and mount["mountpoint"] in ["/", "/var", "/tmp", "/home"]:
                    issues.append(f"Critical filesystem {mount['mountpoint']} mounted read-only")
                
                if "noexec" in options and mount["mountpoint"] in ["/tmp", "/var/tmp"]:
                    issues.append(f"Temp directory {mount['mountpoint']} mounted noexec - may prevent script execution")
                
                if "nosuid" in options and mount["mountpoint"] == "/":
                    issues.append("Root filesystem mounted nosuid - may prevent some system operations")
                
                if issues:
                    mount_with_issues = mount.copy()
                    mount_with_issues["issues"] = issues
                    categories["issues"].append(mount_with_issues)
            
            mounts["categorized"] = categories
        
        # Check disk usage for mounted filesystems
        try:
            df_output = subprocess.run(["df", "-h"], capture_output=True, text=True)
            if df_output.returncode == 0:
                mounts["disk_usage"] = df_output.stdout
                
                # Parse df output for full filesystems
                full_filesystems = []
                for line in df_output.stdout.strip().split('\n')[1:]:  # Skip header
                    parts = line.split()
                    if len(parts) >= 6:
                        try:
                            usage_percent = parts[4].replace('%', '')
                            if usage_percent.isdigit() and int(usage_percent) >= 90:
                                full_filesystems.append({
                                    "filesystem": parts[0],
                                    "mountpoint": parts[5],
                                    "usage": parts[4],
                                    "available": parts[3]
                                })
                        except (ValueError, IndexError):
                            continue
                            
                if full_filesystems:
                    mounts["full_filesystems"] = full_filesystems
        except Exception as e:
            mounts["df_error"] = str(e)
        
        # Check for filesystem errors in dmesg
        try:
            dmesg_fs = subprocess.run(
                ["dmesg", "|", "grep", "-i", "-E", "(filesystem|mount|ext[234]|xfs|btrfs)"],
                capture_output=True, text=True, shell=True
            )
            if dmesg_fs.returncode == 0 and dmesg_fs.stdout.strip():
                mounts["filesystem_dmesg"] = dmesg_fs.stdout
        except Exception:
            pass
        
        # Get mount namespaces info (for containers)
        try:
            with open("/proc/self/mountinfo") as f:
                mounts["mountinfo"] = f.read()
        except Exception as e:
            mounts["mountinfo_error"] = str(e)
        
        # Check for common mount issues
        mount_issues = []
        
        if "mounts_structured" in mounts:
            # Check for duplicate mounts
            mountpoints = [m["mountpoint"] for m in mounts["mounts_structured"]]
            duplicates = [mp for mp in set(mountpoints) if mountpoints.count(mp) > 1]
            if duplicates:
                mount_issues.append(f"Duplicate mount points detected: {duplicates}")
            
            # Check for missing critical mounts
            critical_mounts = ["/", "/proc", "/sys", "/dev"]
            mounted_points = set(mountpoints)
            missing_critical = [cm for cm in critical_mounts if cm not in mounted_points]
            if missing_critical:
                mount_issues.append(f"Missing critical mount points: {missing_critical}")
        
        if mount_issues:
            mounts["mount_issues"] = mount_issues
            
    except Exception as e:
        mounts["error"] = str(e)
    
    return mounts