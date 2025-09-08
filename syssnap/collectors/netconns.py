import subprocess
import shutil
import os


def collect():
    netconns = {}
    try:
        # Use ss (preferred) for network connections
        if shutil.which("ss"):
            try:
                # TCP connections with process info
                ss_tcp = subprocess.run(
                    ["ss", "-tulpn"], 
                    capture_output=True, text=True
                )
                if ss_tcp.returncode == 0:
                    netconns["ss_tcp_udp"] = ss_tcp.stdout
                
                # More detailed TCP state information
                ss_detailed = subprocess.run(
                    ["ss", "-tulpn", "-e", "-m"],
                    capture_output=True, text=True
                )
                if ss_detailed.returncode == 0:
                    netconns["ss_detailed"] = ss_detailed.stdout
                
                # Parse ss output for structured data
                connections = []
                lines = ss_tcp.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        conn_info = {
                            "protocol": parts[0],
                            "state": parts[1] if parts[0] == "tcp" else "N/A",
                            "recv_q": parts[1] if parts[0] == "udp" else parts[2],
                            "send_q": parts[2] if parts[0] == "udp" else parts[3], 
                            "local_address": parts[3] if parts[0] == "udp" else parts[4],
                            "peer_address": parts[4] if parts[0] == "udp" else parts[5] if len(parts) > 5 else "N/A",
                            "process": parts[-1] if "pid=" in parts[-1] else "N/A"
                        }
                        
                        # Extract process name and PID
                        if "pid=" in conn_info["process"]:
                            try:
                                process_part = conn_info["process"]
                                if "users:((" in process_part:
                                    # Parse format: users:(("process_name",pid=1234,fd=5))
                                    process_info = process_part.split("((")[1].split("))")[0]
                                    parts = process_info.split(",")
                                    conn_info["process_name"] = parts[0].strip('"')
                                    for part in parts:
                                        if "pid=" in part:
                                            conn_info["pid"] = part.split("=")[1]
                                        elif "fd=" in part:
                                            conn_info["fd"] = part.split("=")[1]
                            except (IndexError, ValueError):
                                pass
                        
                        connections.append(conn_info)
                
                netconns["connections_structured"] = connections
                
            except Exception as e:
                netconns["ss_error"] = str(e)
        
        # Fallback to netstat if ss is not available
        elif shutil.which("netstat"):
            try:
                netstat = subprocess.run(
                    ["netstat", "-tulpn"],
                    capture_output=True, text=True
                )
                if netstat.returncode == 0:
                    netconns["netstat"] = netstat.stdout
            except Exception as e:
                netconns["netstat_error"] = str(e)
        
        # Get raw socket information from /proc/net/
        proc_net_files = ["tcp", "tcp6", "udp", "udp6"]
        proc_net_data = {}
        
        for net_file in proc_net_files:
            try:
                with open(f"/proc/net/{net_file}") as f:
                    proc_net_data[net_file] = f.read()
            except Exception as e:
                proc_net_data[f"{net_file}_error"] = str(e)
        
        if proc_net_data:
            netconns["proc_net"] = proc_net_data
        
        # Analyze connections for common issues
        if "connections_structured" in netconns:
            analysis = {
                "listening_ports": [],
                "established_connections": [],
                "port_conflicts": [],
                "high_connection_counts": {},
                "suspicious_connections": []
            }
            
            port_usage = {}  # Track which processes use which ports
            
            for conn in netconns["connections_structured"]:
                local_addr = conn.get("local_address", "")
                state = conn.get("state", "")
                process = conn.get("process_name", "unknown")
                
                # Extract port from address
                if ":" in local_addr:
                    try:
                        port = local_addr.split(":")[-1]
                        
                        # Track listening ports
                        if state == "LISTEN" or conn["protocol"] == "udp":
                            analysis["listening_ports"].append({
                                "port": port,
                                "protocol": conn["protocol"],
                                "process": process,
                                "address": local_addr
                            })
                            
                            # Check for port conflicts
                            port_key = f"{conn['protocol']}:{port}"
                            if port_key in port_usage:
                                port_usage[port_key].append(process)
                            else:
                                port_usage[port_key] = [process]
                        
                        # Track established connections
                        elif state == "ESTABLISHED":
                            analysis["established_connections"].append({
                                "local": local_addr,
                                "remote": conn.get("peer_address", ""),
                                "process": process
                            })
                        
                    except (ValueError, IndexError):
                        continue
            
            # Identify port conflicts
            for port_key, processes in port_usage.items():
                if len(processes) > 1:
                    analysis["port_conflicts"].append({
                        "port": port_key,
                        "processes": processes
                    })
            
            # Count connections per process
            process_counts = {}
            for conn in netconns["connections_structured"]:
                process = conn.get("process_name", "unknown")
                process_counts[process] = process_counts.get(process, 0) + 1
            
            # Flag processes with high connection counts
            for process, count in process_counts.items():
                if count > 50:  # Arbitrary threshold
                    analysis["high_connection_counts"][process] = count
            
            # Look for suspicious connections (common malware ports, etc.)
            suspicious_ports = ["4444", "5555", "6666", "31337", "12345"]
            for conn in netconns["connections_structured"]:
                local_addr = conn.get("local_address", "")
                peer_addr = conn.get("peer_address", "")
                
                for susp_port in suspicious_ports:
                    if susp_port in local_addr or susp_port in peer_addr:
                        analysis["suspicious_connections"].append({
                            "connection": conn,
                            "reason": f"Suspicious port {susp_port}"
                        })
            
            netconns["analysis"] = analysis
        
        # Check for common network service ports
        common_services = {
            "22": "SSH",
            "23": "Telnet", 
            "25": "SMTP",
            "53": "DNS",
            "80": "HTTP",
            "110": "POP3",
            "143": "IMAP",
            "443": "HTTPS",
            "993": "IMAPS",
            "995": "POP3S",
            "3306": "MySQL",
            "5432": "PostgreSQL",
            "6379": "Redis",
            "27017": "MongoDB"
        }
        
        if "analysis" in netconns:
            service_mapping = []
            for port_info in netconns["analysis"]["listening_ports"]:
                port = port_info["port"]
                if port in common_services:
                    service_mapping.append({
                        "port": port,
                        "service": common_services[port],
                        "process": port_info["process"],
                        "protocol": port_info["protocol"]
                    })
            
            if service_mapping:
                netconns["service_mapping"] = service_mapping
        
        # Get network interface statistics for context
        try:
            with open("/proc/net/dev") as f:
                netconns["interface_stats"] = f.read()
        except Exception as e:
            netconns["interface_stats_error"] = str(e)
        
        # Check for TIME_WAIT connections (can indicate connection issues)
        if shutil.which("ss"):
            try:
                time_wait = subprocess.run(
                    ["ss", "-tan", "state", "time-wait"],
                    capture_output=True, text=True
                )
                if time_wait.returncode == 0:
                    time_wait_count = len(time_wait.stdout.strip().split('\n')) - 1
                    if time_wait_count > 100:  # High number of TIME_WAIT connections
                        netconns["time_wait_warning"] = {
                            "count": time_wait_count,
                            "data": time_wait.stdout
                        }
            except Exception:
                pass
                
    except Exception as e:
        netconns["error"] = str(e)
    
    return netconns