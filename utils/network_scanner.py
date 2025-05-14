import nmap
import subprocess
import json
from datetime import datetime

def run_nmap_scan(network, options):
    """Run nmap scan with specified options"""
    nm = nmap.PortScanner()
    scan_args = ''
    
    if "Host Discovery" in options:
        scan_args += ' -sn'
    if "Port Scanning" in options:
        scan_args += ' -sS'
    if "OS Detection" in options:
        scan_args += ' -O'
    if "Service Detection" in options:
        scan_args += ' -sV'
        
    results = nm.scan(hosts=network, arguments=scan_args)
    return results

def run_tcpdump_scan(interface, duration=30):
    """Run tcpdump capture"""
    cmd = [
        'sudo', 'tcpdump',
        '-i', interface,
        '-G', str(duration),
        '-W', '1',
        '-w', f'/tmp/capture_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pcap'
    ]
    
    process = subprocess.run(cmd, capture_output=True, text=True)
    return process.stdout

def check_firewall_rules():
    """Check firewall configuration"""
    cmd = ['sudo', 'iptables', '-L', '-n', '-v']
    process = subprocess.run(cmd, capture_output=True, text=True)
    return process.stdout