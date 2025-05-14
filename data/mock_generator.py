import random
import datetime
import pandas as pd
from utils import get_random_ip, get_random_mac

def generate_security_events(num_events=10):
    """
    Generate mock security events for visualization and testing.
    
    Args:
        num_events: Number of events to generate
        
    Returns:
        List of dictionaries containing event data
    """
    event_types = [
        "Login Attempt", 
        "Firewall Block", 
        "IDS Alert", 
        "Authentication Failure", 
        "Malware Detection",
        "Port Scan", 
        "Data Exfiltration", 
        "Privilege Escalation", 
        "Unauthorized Access",
        "Configuration Change"
    ]
    
    severities = ["Low", "Medium", "High", "Critical"]
    severity_weights = [0.4, 0.3, 0.2, 0.1]  # Probability distribution
    
    target_systems = [
        "Web Server", 
        "Database", 
        "File Server", 
        "Active Directory", 
        "Email Server",
        "Application Server", 
        "Firewall", 
        "VPN Gateway", 
        "Workstation",
        "Network Device"
    ]
    
    events = []
    for i in range(num_events):
        # Generate timestamps within last 24 hours
        timestamp = datetime.datetime.now() - datetime.timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        event_type = random.choice(event_types)
        severity = random.choices(severities, severity_weights)[0]
        source_ip = get_random_ip()
        target_system = random.choice(target_systems)
        
        # Create a descriptive message based on event type
        if event_type == "Login Attempt":
            description = f"{'Successful' if random.random() > 0.3 else 'Failed'} login attempt from {source_ip}"
        elif event_type == "Firewall Block":
            description = f"Firewall blocked connection from {source_ip} to port {random.randint(1, 65535)}"
        elif event_type == "IDS Alert":
            description = f"Intrusion detection alert: possible {random.choice(['SQL Injection', 'XSS', 'CSRF', 'Directory Traversal'])} attempt"
        elif event_type == "Authentication Failure":
            description = f"Authentication failure for user '{random.choice(['admin', 'root', 'user', 'service', 'guest'])}' from {source_ip}"
        elif event_type == "Malware Detection":
            description = f"Malware detected: {random.choice(['Trojan', 'Ransomware', 'Spyware', 'Worm', 'Virus'])} on {target_system}"
        elif event_type == "Port Scan":
            description = f"Port scan detected from {source_ip}"
        elif event_type == "Data Exfiltration":
            description = f"Unusual data transfer from {target_system} to {source_ip}"
        elif event_type == "Privilege Escalation":
            description = f"Privilege escalation attempt detected on {target_system}"
        elif event_type == "Unauthorized Access":
            description = f"Unauthorized access to {target_system} from {source_ip}"
        else:  # Configuration Change
            description = f"Configuration change detected on {target_system}"
        
        events.append({
            "event_id": f"EVT-{random.randint(10000, 99999)}",
            "timestamp": timestamp,
            "event_type": event_type,
            "severity": severity,
            "source_ip": source_ip,
            "target_system": target_system,
            "description": description
        })
    
    return events

def generate_system_metrics(num_points=60, server_id=None):
    """
    Generate mock system performance metrics for visualization and testing.
    
    Args:
        num_points: Number of data points to generate
        server_id: Optional server ID to associate with the metrics
        
    Returns:
        List of dictionaries containing system metric data
    """
    metrics = []
    
    # Generate timestamps
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(minutes=num_points)
    timestamps = [start_time + datetime.timedelta(minutes=i) for i in range(num_points)]
    
    # Base values and trends for realistic data generation
    base_cpu = random.uniform(20, 40)
    base_memory = random.uniform(30, 60)
    base_disk = random.uniform(10, 30)
    base_network = random.uniform(20, 50)
    
    # Random trends (increasing, decreasing, or stable)
    cpu_trend = random.uniform(-0.1, 0.1)
    memory_trend = random.uniform(-0.05, 0.1)
    disk_trend = random.uniform(-0.05, 0.05)
    network_trend = random.uniform(-0.1, 0.1)
    
    for i, timestamp in enumerate(timestamps):
        # Apply trends and add noise
        cpu_usage = base_cpu + (i * cpu_trend) + random.uniform(-5, 5)
        memory_usage = base_memory + (i * memory_trend) + random.uniform(-3, 3)
        disk_io = base_disk + (i * disk_trend) + random.uniform(-2, 2)
        network_throughput = base_network + (i * network_trend) + random.uniform(-5, 5)
        
        # Ensure values are within valid ranges
        cpu_usage = max(0.1, min(99.9, cpu_usage))
        memory_usage = max(0.1, min(99.9, memory_usage))
        disk_io = max(0.1, min(99.9, disk_io))
        network_throughput = max(0.1, min(99.9, network_throughput))
        
        metrics.append({
            "timestamp": timestamp,
            "server_id": server_id if server_id else f"srv-{random.randint(1, 10):03d}",
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_io": disk_io,
            "network_throughput": network_throughput
        })
    
    return metrics

def get_network_status():
    """
    Generate a mock network status summary.
    
    Returns:
        Dictionary containing network status metrics
    """
    # Generate overall status based on probabilities
    status_prob = random.random()
    if status_prob > 0.8:
        overall_status = "Healthy"
    elif status_prob > 0.4:
        overall_status = "Warning"
    else:
        overall_status = "Critical"
    
    # Generate supporting metrics
    active_devices = random.randint(50, 200)
    total_devices = active_devices + random.randint(0, 20)
    active_connections = random.randint(500, 2000)
    active_alerts = random.randint(0, 30)
    
    return {
        "Overall Status": overall_status,
        "Active Devices": f"{active_devices}/{total_devices}",
        "Active Connections": active_connections,
        "Active Alerts": active_alerts,
        "Last Updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def generate_network_traffic(hours=24, count=None):
    """
    Generate mock network traffic data for visualization and testing.
    
    Args:
        hours: Number of hours of data to generate
        count: Optional, fixed number of records to generate
        
    Returns:
        List of dictionaries containing network traffic data
    """
    traffic_data = []
    
    # Generate timestamps
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(hours=hours)
    
    if count:
        # If count is specified, generate that many records spread over the time period
        timestamps = [start_time + datetime.timedelta(seconds=random.randint(0, hours*3600)) for _ in range(count)]
        timestamps.sort()
    else:
        # Otherwise use 15-minute intervals
        timestamps = [start_time + datetime.timedelta(minutes=i*15) for i in range(hours*4)]  # 15-minute intervals
    
    # Base values for traffic
    base_inbound = random.uniform(50, 200)
    base_outbound = random.uniform(30, 150)
    
    # Time-of-day effect (business hours have higher traffic)
    for timestamp in timestamps:
        hour = timestamp.hour
        
        # Business hours amplifier (9am-5pm)
        business_factor = 1.5 if 9 <= hour <= 17 else 1.0
        
        # Early morning reduction (midnight to 6am)
        night_factor = 0.6 if 0 <= hour < 6 else 1.0
        
        # Calculate traffic with time factors and noise
        inbound_traffic = base_inbound * business_factor * night_factor + random.uniform(-20, 20)
        outbound_traffic = base_outbound * business_factor * night_factor + random.uniform(-15, 15)
        
        # Ensure non-negative values
        inbound_traffic = max(5, inbound_traffic)
        outbound_traffic = max(3, outbound_traffic)
        
        # Packet loss is typically very low
        packet_loss = random.uniform(0, 2)
        
        # Latency is typically in the range of milliseconds
        latency = random.uniform(5, 50)
        
        source_ip = get_random_ip()
        destination_ip = get_random_ip()
        protocol = random.choice(["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "DNS", "SMTP", "SSH"])
        port = random.randint(1, 65535)
        bytes_transferred = int(max(inbound_traffic, outbound_traffic) * 1024 * 1024 / 8)  # Convert Mbps to bytes
        
        traffic_data.append({
            "timestamp": timestamp,
            "inbound_traffic": inbound_traffic,
            "outbound_traffic": outbound_traffic,
            "packet_loss": packet_loss,
            "latency": latency,
            "source_ip": source_ip,
            "destination_ip": destination_ip,
            "protocol": protocol,
            "port": port,
            "bytes_transferred": bytes_transferred
        })
    
    return traffic_data

def generate_topology_changes(num_changes=20):
    """
    Generate mock network topology changes for visualization and testing.
    
    Args:
        num_changes: Number of changes to generate
        
    Returns:
        List of dictionaries containing topology change data
    """
    change_types = [
        "Device Added", 
        "Device Removed", 
        "Link Added", 
        "Link Removed", 
        "Status Change"
    ]
    
    device_types = [
        "Router", 
        "Switch", 
        "Firewall", 
        "Server", 
        "Access Point", 
        "Workstation"
    ]
    
    changes = []
    
    # Generate changes over the last 30 days
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=30)
    
    for i in range(num_changes):
        timestamp = start_time + datetime.timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        change_type = random.choice(change_types)
        device_type = random.choice(device_types)
        device_id = f"DEV-{random.randint(1000, 9999)}"
        
        # Generate details based on change type
        if change_type == "Device Added":
            ip_address = get_random_ip()
            mac_address = get_random_mac()
            details = f"New {device_type} added with IP {ip_address} and MAC {mac_address}"
        elif change_type == "Device Removed":
            ip_address = get_random_ip()
            details = f"{device_type} with IP {ip_address} has been removed from the network"
        elif change_type == "Link Added":
            src_device = f"DEV-{random.randint(1000, 9999)}"
            details = f"New link established between {device_id} and {src_device}"
        elif change_type == "Link Removed":
            src_device = f"DEV-{random.randint(1000, 9999)}"
            details = f"Link between {device_id} and {src_device} has been removed"
        else:  # Status Change
            old_status = random.choice(["Online", "Offline", "Degraded"])
            new_status = random.choice(["Online", "Offline", "Degraded"])
            while old_status == new_status:
                new_status = random.choice(["Online", "Offline", "Degraded"])
            details = f"{device_type} status changed from {old_status} to {new_status}"
        
        changes.append({
            "change_id": f"CHG-{random.randint(10000, 99999)}",
            "timestamp": timestamp,
            "change_type": change_type,
            "device_id": device_id,
            "device_type": device_type,
            "details": details
        })
    
    return changes

def generate_device_inventory(num_devices=50):
    """
    Generate mock network device inventory for visualization and testing.
    
    Args:
        num_devices: Number of devices to generate
        
    Returns:
        List of dictionaries containing device inventory data
    """
    device_types = [
        "Router", 
        "Switch", 
        "Firewall", 
        "Server", 
        "Access Point", 
        "Workstation",
        "Printer",
        "VoIP Phone",
        "Security Camera",
        "IoT Device"
    ]
    
    manufacturers = [
        "Cisco", 
        "Juniper", 
        "Arista", 
        "HP", 
        "Dell", 
        "Palo Alto",
        "Fortinet",
        "Ubiquiti",
        "Meraki",
        "Check Point"
    ]
    
    models = {
        "Router": ["ISR 4321", "MX250", "SRX340", "FortiGate 100F", "ASR 1001"],
        "Switch": ["Catalyst 9300", "EX4300", "CRS326", "ProCurve 2530", "PowerSwitch N3048"],
        "Firewall": ["ASA 5506-X", "SRX380", "PA-850", "FortiGate 200F", "vSRX"],
        "Server": ["PowerEdge R740", "ProLiant DL380", "ThinkSystem SR650", "UCS C240 M5", "PRIMERGY RX2540"],
        "Access Point": ["Aironet 3800", "UniFi AP-AC-PRO", "Aruba AP-515", "MR46", "WatchGuard AP420"],
        "Workstation": ["OptiPlex 7070", "EliteDesk 800", "ThinkCentre M720", "ProDesk 600", "Precision 3630"],
        "Printer": ["LaserJet Pro M404", "WorkForce Pro WF-C5790", "VersaLink C405", "i-SENSYS MF445dw", "CX825"],
        "VoIP Phone": ["IP Phone 8841", "IP Deskphone J179", "T48S", "6873i", "KX-NT680"],
        "Security Camera": ["AXIS P3245-LV", "DS-2CD2385G1-I", "UVC-G4-PRO", "RLC-511W", "FD9389-HV"],
        "IoT Device": ["ESP32", "Raspberry Pi 4", "Arduino Uno", "Particle Photon", "BeagleBone Black"]
    }
    
    statuses = ["online", "offline", "warning", "maintenance"]
    status_weights = [0.7, 0.1, 0.15, 0.05]  # Probability distribution
    
    networks = ["Corporate", "Guest", "Management", "Production", "Development", "IoT"]
    
    locations = ["HQ", "Branch Office", "Data Center", "Remote Site", "Cloud"]
    
    os_versions = {
        "Router": ["IOS 16.9.3", "IOS-XE 17.3.1", "JunOS 19.4R1", "FortiOS 6.4.5"],
        "Switch": ["IOS 15.2.7", "NXOS 9.3.5", "JunOS 20.2R1", "ArubaOS 8.6.0"],
        "Firewall": ["ASA 9.12.4", "PAN-OS 10.0.6", "FortiOS 7.0.1", "FirePOWER 6.6.0"],
        "Server": ["Windows Server 2019", "Ubuntu 20.04 LTS", "RHEL 8.3", "VMware ESXi 7.0"],
        "Access Point": ["AireOS 8.10.151", "UniFi 6.0.28", "Instant OS 8.7.1", "MR 28.3"],
        "Workstation": ["Windows 10 21H1", "macOS 11.4", "Ubuntu 20.04 Desktop", "Fedora 34"],
        "Printer": ["HP FutureSmart 4.11.0.1", "Epson Firmware 2.63", "Xerox ConnectKey 1.5", "Canon UFR II"],
        "VoIP Phone": ["SIP 8.1.1", "UCS 6.3.0", "PolyOS 5.9.3", "SCCP 10.5.2"],
        "Security Camera": ["AXIS OS 10.4", "Hikvision 4.0", "Dahua 3.71", "Firmware 1.9.2"],
        "IoT Device": ["ESPHome 1.19.2", "Raspberry Pi OS Buster", "Arduino 1.8.13", "Contiki OS 3.0"]
    }
    
    devices = []
    
    for i in range(num_devices):
        device_type = random.choice(device_types)
        manufacturer = random.choice(manufacturers)
        model = random.choice(models.get(device_type, ["Generic Model"]))
        
        status = random.choices(statuses, status_weights)[0]
        network = random.choice(networks)
        location = random.choice(locations)
        
        ip_address = get_random_ip()
        mac_address = get_random_mac()
        
        os_version = random.choice(os_versions.get(device_type, ["Generic OS 1.0"]))
        
        # Last updated typically within the last 7 days
        last_updated = (datetime.datetime.now() - datetime.timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )).strftime("%Y-%m-%d %H:%M:%S")
        
        devices.append({
            "device_id": f"DEV-{i+1:05d}",
            "device_name": f"{location.lower()}-{device_type.lower()}-{i+1:03d}",
            "device_type": device_type,
            "manufacturer": manufacturer,
            "model": model,
            "status": status,
            "ip_address": ip_address,
            "mac_address": mac_address,
            "network": network,
            "location": location,
            "os_version": os_version,
            "last_updated": last_updated
        })
    
    return devices
