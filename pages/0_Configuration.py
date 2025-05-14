import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import re
import ipaddress
import nmap
import os
import json
from database.db_utils import save_network_configuration

# Set page configuration
st.set_page_config(
    page_title="Network Configuration | nSocCSP",
    page_icon="🔧",
    layout="wide"
)

# Page header
st.title("🔧 Network Configuration")
st.subheader("Configure your network monitoring settings")

# Check if we have a configuration
if 'network_config' not in st.session_state:
    st.session_state.network_config = {
        "networks": [],
        "scan_schedule": "hourly",
        "alert_email": "",
        "alert_threshold": "medium",
        "enabled_tools": {
            "nmap": True,
            "tcpdump": True,
            "firewall_audit": True
        }
    }

# Function to validate IP address/range
def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
    
def is_valid_network(network):
    try:
        ipaddress.ip_network(network, strict=False)
        return True
    except ValueError:
        return False

# Create main configuration layout
st.markdown("### General Settings")

col1, col2 = st.columns(2)

with col1:
    scan_schedule = st.selectbox(
        "Scan Schedule",
        options=["real-time", "hourly", "daily", "weekly"],
        index=["real-time", "hourly", "daily", "weekly"].index(st.session_state.network_config["scan_schedule"]),
        help="How frequently to perform automated network scans"
    )
    
    alert_threshold = st.selectbox(
        "Alert Threshold",
        options=["low", "medium", "high", "critical"],
        index=["low", "medium", "high", "critical"].index(st.session_state.network_config["alert_threshold"]),
        help="Minimum severity level for sending alerts"
    )

with col2:
    alert_email = st.text_input(
        "Alert Email",
        value=st.session_state.network_config["alert_email"],
        placeholder="email@example.com",
        help="Email address to receive security alerts"
    )
    
    # Validate email format
    if alert_email and not re.match(r"[^@]+@[^@]+\.[^@]+", alert_email):
        st.warning("Please enter a valid email address")

# Network monitoring configuration
st.markdown("### Network Configuration")
st.markdown("Add the networks and devices you want to monitor")

networks_to_remove = []
for i, network in enumerate(st.session_state.network_config["networks"]):
    cols = st.columns([3, 3, 1, 1])
    with cols[0]:
        network["address"] = st.text_input(
            "Network Address/Range",
            value=network["address"],
            key=f"network_address_{i}",
            placeholder="192.168.1.0/24 or 10.0.0.1-10.0.0.10"
        )
    with cols[1]:
        network["name"] = st.text_input(
            "Network Name",
            value=network["name"],
            key=f"network_name_{i}",
            placeholder="Office LAN"
        )
    with cols[2]:
        network["monitor"] = st.checkbox(
            "Monitor",
            value=network.get("monitor", True),
            key=f"network_monitor_{i}"
        )
    with cols[3]:
        if st.button("Remove", key=f"network_remove_{i}"):
            networks_to_remove.append(i)

# Remove networks marked for removal
for idx in sorted(networks_to_remove, reverse=True):
    st.session_state.network_config["networks"].pop(idx)

# Add new network
st.markdown("#### Add New Network")
new_network_cols = st.columns([3, 3, 2])

with new_network_cols[0]:
    new_address = st.text_input(
        "Network Address/Range",
        key="new_network_address",
        placeholder="192.168.1.0/24 or 10.0.0.1-10.0.0.10"
    )
    
    # Validate IP/network format
    is_valid = False
    if new_address:
        if "/" in new_address:  # CIDR notation
            is_valid = is_valid_network(new_address)
        elif "-" in new_address:  # Range notation
            start_ip, end_ip = new_address.split("-")
            is_valid = is_valid_ip(start_ip.strip()) and is_valid_ip(end_ip.strip())
        else:  # Single IP
            is_valid = is_valid_ip(new_address)
            
        if not is_valid:
            st.warning("Please enter a valid IP address, range, or network in CIDR notation")

with new_network_cols[1]:
    new_name = st.text_input(
        "Network Name",
        key="new_network_name",
        placeholder="Office LAN"
    )

with new_network_cols[2]:
    if st.button("Add Network") and new_address and new_name and is_valid:
        st.session_state.network_config["networks"].append({
            "address": new_address,
            "name": new_name,
            "monitor": True
        })
        # Clear inputs
        st.rerun()

# Tools configuration
st.markdown("### Tools Configuration")
st.markdown("Enable or disable specific monitoring tools")

tool_cols = st.columns(3)

with tool_cols[0]:
    nmap_enabled = st.checkbox(
        "Enable Nmap",
        value=st.session_state.network_config["enabled_tools"]["nmap"],
        help="Network scanning and port discovery"
    )
    
    if nmap_enabled:
        nmap_options = st.multiselect(
            "Nmap Functions",
            options=["Host Discovery", "Port Scanning", "OS Detection", "Service Detection", "Firewall/IDS Evasion"],
            default=["Host Discovery", "Port Scanning"],
            key="nmap_functions"
        )

with tool_cols[1]:
    tcpdump_enabled = st.checkbox(
        "Enable tcpdump",
        value=st.session_state.network_config["enabled_tools"]["tcpdump"],
        help="Network packet capture and analysis"
    )
    
    if tcpdump_enabled:
        tcpdump_options = st.multiselect(
            "tcpdump Options",
            options=["HTTP Traffic", "DNS Queries", "ICMP Traffic", "TCP Connections", "Custom Filters"],
            default=["HTTP Traffic", "DNS Queries"],
            key="tcpdump_options"
        )

with tool_cols[2]:
    firewall_audit = st.checkbox(
        "Enable Firewall Auditing",
        value=st.session_state.network_config["enabled_tools"]["firewall_audit"],
        help="Audit firewall rules and configurations"
    )
    
    if firewall_audit:
        firewall_options = st.multiselect(
            "Firewall Audit Options",
            options=["Rule Consistency", "Default Policies", "Unused Rules", "Overlapping Rules"],
            default=["Rule Consistency", "Default Policies"],
            key="firewall_options"
        )

# Custom scripts and integrations
st.markdown("### Advanced Settings")

# Save data
if st.button("Save Configuration", type="primary"):
    try:
        # Update session state
        st.session_state.network_config.update({
            "scan_schedule": scan_schedule,
            "alert_email": alert_email,
            "alert_threshold": alert_threshold,
            "enabled_tools": {
                "nmap": nmap_enabled,
                "tcpdump": tcpdump_enabled,
                "firewall_audit": firewall_audit
            }
        })
        
        if nmap_enabled:
            st.session_state.network_config["enabled_tools"]["nmap_options"] = nmap_options
        if tcpdump_enabled:
            st.session_state.network_config["enabled_tools"]["tcpdump_options"] = tcpdump_options
        if firewall_audit:
            st.session_state.network_config["enabled_tools"]["firewall_options"] = firewall_options
        
        # Save to database
        save_network_configuration(st.session_state.network_config)
        
        # Save to file for backup
        with open("network_config.json", "w") as f:
            json.dump(st.session_state.network_config, f, indent=4)
            
        st.success("Configuration saved successfully!")
    except Exception as e:
        st.error(f"Error saving configuration: {str(e)}")

# Test scan functionality if available networks
if st.session_state.network_config["networks"]:
    st.markdown("### Test Network Scan")
    
    test_network = st.selectbox(
        "Select Network to Test",
        options=[f"{net['name']} ({net['address']})" for net in st.session_state.network_config["networks"] if net["monitor"]],
        key="test_network"
    )
    
    if test_network and st.button("Run Test Scan"):
        selected_network = next(net for net in st.session_state.network_config["networks"] 
                            if f"{net['name']} ({net['address']})" == test_network)
        
        with st.spinner(f"Scanning network {selected_network['name']}..."):
            try:
                if nmap_enabled:
                    # Note: Nmap might require elevated privileges for some scans
                    st.info("Using Python-Nmap module for scanning (limited functionality in a web interface)")
                    
                    nm = nmap.PortScanner()
                    
                    # We'll do a simple ping scan which doesn't require root/admin
                    results = nm.scan(hosts=selected_network['address'], arguments='-sn')
                    
                    # Show results
                    hosts_found = len(nm.all_hosts())
                    st.success(f"Scan completed! Found {hosts_found} active hosts.")
                    
                    if hosts_found > 0:
                        hosts_data = []
                        for host in nm.all_hosts():
                            try:
                                hostname = nm[host].hostname() if 'hostname' in nm[host] else 'Unknown'
                                status = nm[host]['status']['state'] if 'status' in nm[host] else 'Unknown'
                                hosts_data.append({
                                    "IP Address": host,
                                    "Hostname": hostname,
                                    "Status": status
                                })
                            except:
                                # Handle possible errors in parsing the host data
                                hosts_data.append({
                                    "IP Address": host,
                                    "Hostname": "Error retrieving hostname",
                                    "Status": "Unknown"
                                })
                        
                        hosts_df = pd.DataFrame(hosts_data)
                        st.dataframe(hosts_df)
                    else:
                        st.warning("No active hosts found in the specified network.")
                else:
                    st.warning("Enable Nmap in the tools configuration to perform test scans.")
            except Exception as e:
                st.error(f"Error during network scan: {str(e)}")
                st.info("Note: Some scan types may require root/administrator privileges.")

# Footer
st.divider()
st.caption("© 2025 - nSocCSP | Configuration Module | Last updated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))