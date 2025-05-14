import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import time
import random
from utils import load_image, format_size
from data.mock_generator import generate_network_traffic

# Set page configuration
st.set_page_config(
    page_title="Network Traffic | nSocCSP",
    page_icon="🚦",
    layout="wide"
)

# Page header
st.title("🚦 Network Traffic")
st.subheader("Monitor and analyze network traffic patterns to detect anomalies and potential threats")

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Traffic Overview", "Protocol Analysis", "Flow Monitoring"])

with tab1:
    # Traffic Overview
    st.subheader("Network Traffic Overview")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_bandwidth = random.randint(500, 2000)
        st.metric(label="Total Bandwidth (Mbps)", value=total_bandwidth, delta=f"{random.choice([-5, -2, 0, 3, 5])}%")
        
    with col2:
        active_connections = random.randint(1000, 5000)
        st.metric(label="Active Connections", value=active_connections, delta=f"{random.choice([-100, -50, 0, 75, 150])}")
        
    with col3:
        packet_loss = round(random.uniform(0.01, 1.50), 2)
        st.metric(label="Packet Loss (%)", value=packet_loss, delta=f"{random.choice([-0.2, -0.1, 0, 0.1, 0.2])}")
        
    with col4:
        latency = random.randint(5, 50)
        st.metric(label="Avg. Latency (ms)", value=latency, delta=f"{random.choice([-5, -2, 0, 3, 5])}")
    
    # Generate traffic data for the charts
    traffic_data = generate_network_traffic(48)  # 48 hours of data
    traffic_df = pd.DataFrame(traffic_data)
    
    # Format timestamp for better display
    traffic_df['datetime'] = pd.to_datetime(traffic_df['timestamp'])
    
    # Traffic Over Time Chart
    st.subheader("Network Traffic Over Time")
    
    # Create a line chart with inbound and outbound traffic
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=traffic_df['datetime'],
        y=traffic_df['inbound_traffic'],
        mode='lines',
        name='Inbound',
        line=dict(color='blue', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=traffic_df['datetime'],
        y=traffic_df['outbound_traffic'],
        mode='lines',
        name='Outbound',
        line=dict(color='green', width=2)
    ))
    
    fig.update_layout(
        title='Network Traffic (Last 48 Hours)',
        xaxis_title='Time',
        yaxis_title='Traffic (Mbps)',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Traffic by Network Segment
    st.subheader("Traffic by Network Segment")
    
    segments = ['Internal', 'DMZ', 'External', 'Cloud', 'VPN']
    inbound_values = [random.randint(50, 500) for _ in segments]
    outbound_values = [random.randint(50, 500) for _ in segments]
    
    segment_df = pd.DataFrame({
        'Network Segment': segments,
        'Inbound': inbound_values,
        'Outbound': outbound_values
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=segment_df['Network Segment'],
        y=segment_df['Inbound'],
        name='Inbound',
        marker_color='blue'
    ))
    
    fig.add_trace(go.Bar(
        x=segment_df['Network Segment'],
        y=segment_df['Outbound'],
        name='Outbound',
        marker_color='green'
    ))
    
    fig.update_layout(
        title='Traffic by Network Segment',
        xaxis_title='Network Segment',
        yaxis_title='Traffic (Mbps)',
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Top Talkers
    st.subheader("Top Talkers (Source IPs)")
    
    # Generate some random IP addresses for the top talkers
    top_ips = [f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}" for _ in range(10)]
    traffic_values = [random.randint(100, 1000) for _ in range(10)]
    
    talkers_df = pd.DataFrame({
        'Source IP': top_ips,
        'Traffic (Mbps)': traffic_values
    }).sort_values('Traffic (Mbps)', ascending=False)
    
    fig = px.bar(
        talkers_df,
        x='Source IP',
        y='Traffic (Mbps)',
        color='Traffic (Mbps)',
        color_continuous_scale='Viridis',
        title='Top 10 Source IPs by Traffic Volume'
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Protocol Analysis
    st.subheader("Protocol Analysis")
    
    # Protocol Distribution
    st.markdown("### Traffic by Protocol")
    
    protocols = ['HTTP', 'HTTPS', 'DNS', 'SMTP', 'SSH', 'FTP', 'SNMP', 'Other']
    protocol_values = [random.randint(50, 500) for _ in protocols]
    total_protocol = sum(protocol_values)
    protocol_percentages = [round((v / total_protocol) * 100, 1) for v in protocol_values]
    
    protocol_df = pd.DataFrame({
        'Protocol': protocols,
        'Traffic (Mbps)': protocol_values,
        'Percentage': protocol_percentages
    })
    
    fig = px.pie(
        protocol_df,
        values='Traffic (Mbps)',
        names='Protocol',
        title='Protocol Distribution',
        hover_data=['Percentage'],
        labels={'Percentage': 'Percentage (%)'},
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Port Activity
    st.markdown("### Top Active Ports")
    
    ports = [80, 443, 22, 53, 25, 3389, 20, 21, 161, 445]
    port_names = ['HTTP', 'HTTPS', 'SSH', 'DNS', 'SMTP', 'RDP', 'FTP-Data', 'FTP', 'SNMP', 'SMB']
    port_traffic = [random.randint(50, 500) for _ in ports]
    
    port_df = pd.DataFrame({
        'Port': ports,
        'Service': port_names,
        'Traffic (Mbps)': port_traffic
    }).sort_values('Traffic (Mbps)', ascending=False)
    
    # Create a combined label
    port_df['Port_Service'] = port_df['Port'].astype(str) + ' (' + port_df['Service'] + ')'
    
    fig = px.bar(
        port_df,
        x='Port_Service',
        y='Traffic (Mbps)',
        color='Traffic (Mbps)',
        color_continuous_scale='Viridis',
        title='Top Active Ports by Traffic Volume'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Protocol Anomaly Detection
    st.markdown("### Protocol Anomaly Detection")
    
    # Generate some sample anomalies
    anomaly_protocols = random.sample(protocols, 3)
    anomaly_times = [
        (datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 24))).strftime("%Y-%m-%d %H:%M:%S")
        for _ in range(3)
    ]
    anomaly_descs = [
        "Unusual spike in traffic volume",
        "Abnormal connection pattern detected",
        "Suspicious port scanning activity"
    ]
    anomaly_severities = [random.choice(['Low', 'Medium', 'High']) for _ in range(3)]
    
    anomaly_df = pd.DataFrame({
        'Timestamp': anomaly_times,
        'Protocol': anomaly_protocols,
        'Description': anomaly_descs,
        'Severity': anomaly_severities
    })
    
    # Apply styling to the dataframe
    def highlight_severity(val):
        if val == 'High':
            return 'background-color: red; color: white'
        elif val == 'Medium':
            return 'background-color: orange'
        else:
            return 'background-color: green; color: white'
    
    # Apply the styling
    styled_df = anomaly_df.style.map(
        highlight_severity, 
        subset=['Severity']
    )
    
    st.dataframe(styled_df, use_container_width=True)

with tab3:
    # Flow Monitoring
    st.subheader("Network Flow Monitoring")
    
    # Flow Statistics
    st.markdown("### Network Flow Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Flow count over time
        timestamps = pd.date_range(start=datetime.datetime.now() - datetime.timedelta(hours=24), 
                                   end=datetime.datetime.now(), 
                                   freq='h')
        flow_counts = [random.randint(1000, 5000) for _ in range(len(timestamps))]
        
        flow_df = pd.DataFrame({
            'Timestamp': timestamps,
            'Flow Count': flow_counts
        })
        
        fig = px.line(
            flow_df,
            x='Timestamp',
            y='Flow Count',
            title='Flow Count Over Time',
            color_discrete_sequence=['blue']
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Flow duration distribution
        durations = [random.randint(1, 3600) for _ in range(1000)]  # 1 second to 1 hour
        
        duration_df = pd.DataFrame({
            'Duration (seconds)': durations
        })
        
        fig = px.histogram(
            duration_df,
            x='Duration (seconds)',
            nbins=20,
            title='Flow Duration Distribution',
            color_discrete_sequence=['green']
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Geographical Flow Visualization
    st.markdown("### Geographical Flow Distribution")
    
    # Create some sample country data
    countries = ['United States', 'China', 'Russia', 'Germany', 'Brazil', 'India', 'United Kingdom', 'Japan', 'Canada', 'Australia']
    inbound_flows = [random.randint(100, 1000) for _ in countries]
    outbound_flows = [random.randint(100, 1000) for _ in countries]
    
    geo_df = pd.DataFrame({
        'Country': countries,
        'Inbound Flows': inbound_flows,
        'Outbound Flows': outbound_flows
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=geo_df['Country'],
        y=geo_df['Inbound Flows'],
        name='Inbound',
        marker_color='blue'
    ))
    
    fig.add_trace(go.Bar(
        x=geo_df['Country'],
        y=geo_df['Outbound Flows'],
        name='Outbound',
        marker_color='green'
    ))
    
    fig.update_layout(
        title='Flow Distribution by Country',
        xaxis_title='Country',
        yaxis_title='Flow Count',
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Flow Size Distribution
    st.markdown("### Flow Size Distribution")
    
    # Generate random flow sizes (in KB)
    flow_sizes = [random.randint(1, 10000) for _ in range(1000)]
    
    size_df = pd.DataFrame({
        'Flow Size (KB)': flow_sizes
    })
    
    fig = px.histogram(
        size_df,
        x='Flow Size (KB)',
        nbins=25,
        log_y=True,  # Use log scale for better visualization
        title='Flow Size Distribution (Log Scale)',
        color_discrete_sequence=['purple']
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
st.caption("© 2025 - nSocCSP | Network Traffic Module | Last updated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
