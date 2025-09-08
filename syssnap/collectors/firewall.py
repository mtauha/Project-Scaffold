import subprocess
import shutil


def collect():
    firewall = {}
    try:
        # Check for iptables
        if shutil.which("iptables"):
            try:
                # Get iptables rules with verbose output
                iptables_list = subprocess.run(
                    ["iptables", "-L", "-n", "-v"], 
                    capture_output=True, text=True
                )
                if iptables_list.returncode == 0:
                    firewall["iptables_list"] = iptables_list.stdout
                
                # Get NAT table rules
                iptables_nat = subprocess.run(
                    ["iptables", "-t", "nat", "-L", "-n", "-v"],
                    capture_output=True, text=True
                )
                if iptables_nat.returncode == 0:
                    firewall["iptables_nat"] = iptables_nat.stdout
                
                # Get mangle table rules
                iptables_mangle = subprocess.run(
                    ["iptables", "-t", "mangle", "-L", "-n", "-v"],
                    capture_output=True, text=True
                )
                if iptables_mangle.returncode == 0:
                    firewall["iptables_mangle"] = iptables_mangle.stdout
                    
                # Get raw table rules  
                iptables_raw = subprocess.run(
                    ["iptables", "-t", "raw", "-L", "-n", "-v"],
                    capture_output=True, text=True
                )
                if iptables_raw.returncode == 0:
                    firewall["iptables_raw"] = iptables_raw.stdout
                    
            except Exception as e:
                firewall["iptables_error"] = str(e)
        
        # Check for ip6tables (IPv6)
        if shutil.which("ip6tables"):
            try:
                ip6tables_list = subprocess.run(
                    ["ip6tables", "-L", "-n", "-v"],
                    capture_output=True, text=True
                )
                if ip6tables_list.returncode == 0:
                    firewall["ip6tables_list"] = ip6tables_list.stdout
            except Exception as e:
                firewall["ip6tables_error"] = str(e)
        
        # Check for UFW (Uncomplicated Firewall)
        if shutil.which("ufw"):
            try:
                ufw_status = subprocess.run(
                    ["ufw", "status", "verbose"],
                    capture_output=True, text=True
                )
                if ufw_status.returncode == 0:
                    firewall["ufw_status"] = ufw_status.stdout
                
                # Get numbered rules for easier troubleshooting
                ufw_numbered = subprocess.run(
                    ["ufw", "status", "numbered"],
                    capture_output=True, text=True
                )
                if ufw_numbered.returncode == 0:
                    firewall["ufw_numbered"] = ufw_numbered.stdout
                    
            except Exception as e:
                firewall["ufw_error"] = str(e)
        
        # Check for firewalld
        if shutil.which("firewall-cmd"):
            try:
                # Check if firewalld is running
                firewalld_state = subprocess.run(
                    ["firewall-cmd", "--state"],
                    capture_output=True, text=True
                )
                firewall["firewalld_state"] = firewalld_state.stdout.strip()
                
                if firewalld_state.returncode == 0:
                    # Get default zone
                    default_zone = subprocess.run(
                        ["firewall-cmd", "--get-default-zone"],
                        capture_output=True, text=True
                    )
                    firewall["firewalld_default_zone"] = default_zone.stdout.strip()
                    
                    # Get active zones
                    active_zones = subprocess.run(
                        ["firewall-cmd", "--get-active-zones"],
                        capture_output=True, text=True
                    )
                    firewall["firewalld_active_zones"] = active_zones.stdout
                    
                    # List all zones and their rules
                    zones_list = subprocess.run(
                        ["firewall-cmd", "--list-all-zones"],
                        capture_output=True, text=True
                    )
                    firewall["firewalld_all_zones"] = zones_list.stdout
                    
                    # Get services
                    services = subprocess.run(
                        ["firewall-cmd", "--list-services"],
                        capture_output=True, text=True
                    )
                    firewall["firewalld_services"] = services.stdout.strip()
                    
                    # Get ports
                    ports = subprocess.run(
                        ["firewall-cmd", "--list-ports"],
                        capture_output=True, text=True
                    )
                    firewall["firewalld_ports"] = ports.stdout.strip()
                    
            except Exception as e:
                firewall["firewalld_error"] = str(e)
        
        # Check for nftables (newer netfilter framework)
        if shutil.which("nft"):
            try:
                nft_list = subprocess.run(
                    ["nft", "list", "ruleset"],
                    capture_output=True, text=True
                )
                if nft_list.returncode == 0:
                    firewall["nftables_rules"] = nft_list.stdout
            except Exception as e:
                firewall["nftables_error"] = str(e)
        
        # Check for common ports listening (for context)
        if shutil.which("ss"):
            try:
                listening_ports = subprocess.run(
                    ["ss", "-tuln"],
                    capture_output=True, text=True
                )
                if listening_ports.returncode == 0:
                    firewall["listening_ports"] = listening_ports.stdout
            except Exception:
                # Fallback to netstat if available
                if shutil.which("netstat"):
                    try:
                        netstat_ports = subprocess.run(
                            ["netstat", "-tuln"],
                            capture_output=True, text=True
                        )
                        if netstat_ports.returncode == 0:
                            firewall["listening_ports"] = netstat_ports.stdout
                    except Exception:
                        pass
        
        # Check for fail2ban status (common security tool)
        if shutil.which("fail2ban-client"):
            try:
                fail2ban_status = subprocess.run(
                    ["fail2ban-client", "status"],
                    capture_output=True, text=True
                )
                if fail2ban_status.returncode == 0:
                    firewall["fail2ban_status"] = fail2ban_status.stdout
            except Exception as e:
                firewall["fail2ban_error"] = str(e)
        
        # Parse iptables for common issues
        if "iptables_list" in firewall:
            issues = []
            rules = firewall["iptables_list"]
            
            # Check for default DROP policies
            if "policy DROP" in rules:
                issues.append("Default DROP policy detected - may block traffic")
            
            # Check for REJECT rules
            if "REJECT" in rules:
                issues.append("REJECT rules present - may cause connection refused errors")
                
            # Check for common service blocks
            common_ports = ["22", "80", "443", "3306", "5432", "6379"]
            for port in common_ports:
                if f"dpt:{port}" in rules and "DROP" in rules:
                    issues.append(f"Port {port} may be blocked")
                    
            if issues:
                firewall["potential_issues"] = issues
                
    except Exception as e:
        firewall["error"] = str(e)
    
    return firewall