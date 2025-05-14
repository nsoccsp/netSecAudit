import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import random
import networkx as nx

def network_health_summary():
    """
    Display a summary of network health metrics.
    """
    # Metrics for the network health
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        uptime = random.randint(99, 100)
        st.metric("Network Uptime", f"{uptime}%", f"{random.choice([0, 0.1, 0.2])}%")
        
    with col2:
        latency = random.randint(5, 30)
        st.metric("Avg. Latency", f"{latency} ms", f"{random.choice([-5, -2, 0, 1, 2])}")
        
    with col3:
        packet_loss = round(random.uniform(0, 0.5), 2)
        st.metric("Packet Loss", f"{packet_loss}%", f"{random.choice([-0.1, -0.05, 0, 0.1])}%")
        
    with col4:
        bandwidth_usage = random.randint(40, 80)
        st.metric("Bandwidth Usage", f"{bandwidth_usage}%", f"{random.choice([-5, -2, 0, 3, 5])}%")

def traffic_flow_visualization():
    """
    Create a visualization of network traffic flows.
    """
    st.subheader("Network Traffic Flow")
    
    # Generate sample time-series data for network traffic
    timestamps = pd.date_range(
        start=datetime.datetime.now() - datetime.timedelta(hours=24),
        end=datetime.datetime.now(),
        freq='15min'
    )
    
    # Generate some random traffic data with realistic patterns
    traffic_base = 100  # Base traffic level
    traffic_variation = 50  # Random variation
    time_effect = [0.5, 0.4, 0.3, 0.3, 0.4, 0.5, 0.7, 1.0, 1.2, 1.3, 1.2, 1.0,  # Hours 0-11
                  0.9, 0.8, 0.7, 0.8, 0.9, 1.1, 1.3, 1.2, 1.0, 0.8, 0.7, 0.6]  # Hours 12-23
    
    inbound_traffic = []
    outbound_traffic = []
    
    for ts in timestamps:
        hour_factor = time_effect[ts.hour]
        base_traffic = traffic_base * hour_factor
        
        inbound = base_traffic + random.uniform(-traffic_variation, traffic_variation)
        outbound = base_traffic * 0.7 + random.uniform(-traffic_variation, traffic_variation)
        
        inbound_traffic.append(max(0, inbound))
        outbound_traffic.append(max(0, outbound))
    
    # Create the DataFrame
    traffic_df = pd.DataFrame({
        'timestamp': timestamps,
        'inbound': inbound_traffic,
        'outbound': outbound_traffic
    })
    
    # Create the visualization
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=traffic_df['timestamp'],
        y=traffic_df['inbound'],
        mode='lines',
        name='Inbound',
        line=dict(color='blue', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=traffic_df['timestamp'],
        y=traffic_df['outbound'],
        mode='lines',
        name='Outbound',
        line=dict(color='green', width=2)
    ))
    
    fig.update_layout(
        title='Network Traffic Flow (Last 24 Hours)',
        xaxis_title='Time',
        yaxis_title='Traffic (Mbps)',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def protocol_distribution_chart():
    """
    Display a chart showing the distribution of network protocols.
    """
    # Define common protocols
    protocols = ['HTTP/HTTPS', 'DNS', 'SMTP/IMAP', 'SSH/SCP', 'FTP', 'RDP', 'SMB/CIFS', 'SNMP', 'Other']
    
    # Generate random distribution (more realistic)
    http_pct = random.uniform(40, 60)
    dns_pct = random.uniform(10, 20)
    mail_pct = random.uniform(5, 15)
    ssh_pct = random.uniform(3, 8)
    ftp_pct = random.uniform(1, 5)
    rdp_pct = random.uniform(2, 7)
    smb_pct = random.uniform(3, 10)
    snmp_pct = random.uniform(1, 3)
    
    # Normalize to ensure sum is 100
    total = http_pct + dns_pct + mail_pct + ssh_pct + ftp_pct + rdp_pct + smb_pct + snmp_pct
    remaining = 100 - total
    
    values = [
        http_pct,
        dns_pct,
        mail_pct,
        ssh_pct,
        ftp_pct,
        rdp_pct,
        smb_pct,
        snmp_pct,
        max(0, remaining)  # Ensure non-negative
    ]
    
    # Create DataFrame
    protocol_df = pd.DataFrame({
        'Protocol': protocols,
        'Percentage': values
    })
    
    # Create pie chart
    fig = px.pie(
        protocol_df,
        values='Percentage',
        names='Protocol',
        title='Network Traffic by Protocol',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig, use_container_width=True)

def top_talkers_chart(n_talkers=10):
    """
    Display a chart of the top network talkers (devices with highest traffic).
    
    Args:
        n_talkers: Number of top talkers to display
    """
    # Generate synthetic data for top talkers
    ip_addresses = [f"192.168.1.{random.randint(2, 254)}" for _ in range(n_talkers)]
    traffic_values = [round(random.uniform(50, 500), 1) for _ in range(n_talkers)]
    
    # Create a role/device type for each IP for better context
    device_types = []
    for _ in range(n_talkers):
        device_type = random.choice([
            "Workstation", "Server", "Database", "Printer", 
            "IoT Device", "VoIP Phone", "Security Camera"
        ])
        device_types.append(device_type)
    
    # Create DataFrame
    talkers_df = pd.DataFrame({
        'IP Address': ip_addresses,
        'Device Type': device_types,
        'Traffic (MB)': traffic_values
    }).sort_values('Traffic (MB)', ascending=False)
    
    # Create the bar chart
    fig = px.bar(
        talkers_df,
        x='IP Address',
        y='Traffic (MB)',
        color='Device Type',
        title=f'Top {n_talkers} Network Talkers',
        hover_data=['Device Type', 'Traffic (MB)']
    )
    
    st.plotly_chart(fig, use_container_width=True)

def network_interface_status():
    """
    Display a table showing the status of network interfaces.
    """
    st.subheader("Network Interface Status")
    
    # Generate sample network interfaces
    interfaces = []
    for i in range(10):
        interface_type = random.choice(['Ethernet', 'WiFi', 'VLAN', 'WAN', 'Trunk'])
        interface_name = f"{interface_type}{i+1}"
        speed = random.choice([100, 1000, 10000])
        
        if random.random() < 0.8:  # 80% interfaces are up
            status = "Up"
            utilization = round(random.uniform(10, 80), 1)
        else:
            status = random.choice(["Down", "Disabled"])
            utilization = 0
        
        errors = random.randint(0, 100) if status == "Up" else 0
        
        interfaces.append({
            "Interface": interface_name,
            "Type": interface_type,
            "Speed (Mbps)": speed,
            "Status": status,
            "Utilization (%)": utilization,
            "Errors": errors
        })
    
    # Create DataFrame
    interfaces_df = pd.DataFrame(interfaces)
    
    # Apply styling to the dataframe
    def highlight_status(val):
        if val == "Up":
            return 'background-color: green; color: white'
        elif val == "Down":
            return 'background-color: red; color: white'
        else:
            return 'background-color: gray; color: white'
    
    def highlight_utilization(val):
        if isinstance(val, (int, float)):
            if val > 70:
                return 'background-color: rgba(255, 0, 0, 0.2)'
            elif val > 50:
                return 'background-color: rgba(255, 165, 0, 0.2)'
            elif val > 0:
                return 'background-color: rgba(0, 128, 0, 0.1)'
        return ''
    
    # Apply the styling
    styled_df = interfaces_df.style.applymap(
        highlight_status, 
        subset=['Status']
    ).applymap(
        highlight_utilization,
        subset=['Utilization (%)']
    )
    
    st.dataframe(styled_df, use_container_width=True)
