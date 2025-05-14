import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import time
import random
from utils import load_image
from data.mock_generator import generate_system_metrics

# Set page configuration
st.set_page_config(
    page_title="System Performance | nSocCSP",
    page_icon="💻",
    layout="wide"
)

# Page header
st.title("💻 System Performance")
st.subheader("Monitor system resources utilization across your network infrastructure")

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Resource Dashboard", "Server Metrics", "Performance Alerts"])

with tab1:
    # Resource Dashboard
    st.subheader("Resource Utilization Dashboard")
    
    # Select time range
    time_range = st.selectbox(
        "Select Time Range",
        options=["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days"],
        index=1
    )
    
    # Map selection to number of data points
    time_map = {
        "Last Hour": 60,
        "Last 6 Hours": 72,
        "Last 24 Hours": 144,
        "Last 7 Days": 168
    }
    
    data_points = time_map[time_range]
    
    # Generate system metrics data
    system_data = generate_system_metrics(data_points)
    system_df = pd.DataFrame(system_data)
    
    # Format timestamp for better display
    system_df['datetime'] = pd.to_datetime(system_df['timestamp'])
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_cpu = round(system_df['cpu_usage'].mean(), 1)
        st.metric(label="Avg. CPU Usage (%)", value=avg_cpu, delta=f"{round(random.uniform(-5, 5), 1)}")
        
    with col2:
        avg_memory = round(system_df['memory_usage'].mean(), 1)
        st.metric(label="Avg. Memory Usage (%)", value=avg_memory, delta=f"{round(random.uniform(-3, 3), 1)}")
        
    with col3:
        avg_disk = round(system_df['disk_io'].mean(), 1)
        st.metric(label="Avg. Disk I/O (%)", value=avg_disk, delta=f"{round(random.uniform(-4, 4), 1)}")
        
    with col4:
        avg_network = round(system_df['network_throughput'].mean(), 1)
        st.metric(label="Avg. Network Throughput (Mbps)", value=avg_network, delta=f"{round(random.uniform(-10, 10), 1)}")
    
    # CPU, Memory, and Disk Usage Chart
    st.subheader("System Resource Utilization")
    
    # Create a line chart with CPU, memory, and disk
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=system_df['datetime'],
        y=system_df['cpu_usage'],
        mode='lines',
        name='CPU Usage (%)',
        line=dict(color='blue', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=system_df['datetime'],
        y=system_df['memory_usage'],
        mode='lines',
        name='Memory Usage (%)',
        line=dict(color='green', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=system_df['datetime'],
        y=system_df['disk_io'],
        mode='lines',
        name='Disk I/O (%)',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title=f'System Resource Utilization ({time_range})',
        xaxis_title='Time',
        yaxis_title='Usage (%)',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Network Throughput Chart
    st.subheader("Network Throughput")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=system_df['datetime'],
        y=system_df['network_throughput'],
        mode='lines',
        name='Network Throughput',
        line=dict(color='purple', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title=f'Network Throughput ({time_range})',
        xaxis_title='Time',
        yaxis_title='Throughput (Mbps)',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # System Load Distribution
    st.subheader("System Load Distribution")
    
    # Generate sample load data for multiple servers
    server_names = [f"srv-{i:03d}" for i in range(1, 11)]
    cpu_loads = [random.uniform(10, 90) for _ in range(10)]
    memory_loads = [random.uniform(20, 85) for _ in range(10)]
    
    load_df = pd.DataFrame({
        'Server': server_names,
        'CPU Load (%)': cpu_loads,
        'Memory Load (%)': memory_loads
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=load_df['Server'],
        y=load_df['CPU Load (%)'],
        name='CPU Load',
        marker_color='blue'
    ))
    
    fig.add_trace(go.Bar(
        x=load_df['Server'],
        y=load_df['Memory Load (%)'],
        name='Memory Load',
        marker_color='green'
    ))
    
    fig.update_layout(
        title='System Load by Server',
        xaxis_title='Server',
        yaxis_title='Load (%)',
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Server Metrics
    st.subheader("Server Performance Metrics")
    
    # Server selection
    servers = [f"srv-{i:03d}" for i in range(1, 21)]
    selected_server = st.selectbox("Select Server", options=servers)
    
    # Generate detailed metrics for the selected server
    server_data = generate_system_metrics(100, server_id=selected_server)
    server_df = pd.DataFrame(server_data)
    server_df['datetime'] = pd.to_datetime(server_df['timestamp'])
    
    # Server info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Server ID:** {selected_server}")
        
    with col2:
        server_role = random.choice(["Web Server", "Database Server", "Application Server", "File Server", "Domain Controller"])
        st.info(f"**Role:** {server_role}")
        
    with col3:
        uptime = random.randint(1, 500)
        st.info(f"**Uptime:** {uptime} days")
    
    # Current metrics
    st.subheader("Current Resource Utilization")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_cpu = server_df['cpu_usage'].iloc[-1]
        st.metric(label="CPU Usage (%)", value=round(current_cpu, 1), 
                 delta=f"{round(current_cpu - server_df['cpu_usage'].iloc[-2], 1)}")
        
        # CPU usage gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=current_cpu,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "CPU Usage"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "blue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgreen"},
                    {'range': [50, 80], 'color': "orange"},
                    {'range': [80, 100], 'color': "red"}
                ]
            }
        ))
        
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        current_memory = server_df['memory_usage'].iloc[-1]
        st.metric(label="Memory Usage (%)", value=round(current_memory, 1), 
                 delta=f"{round(current_memory - server_df['memory_usage'].iloc[-2], 1)}")
        
        # Memory usage gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=current_memory,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Memory Usage"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgreen"},
                    {'range': [50, 80], 'color': "orange"},
                    {'range': [80, 100], 'color': "red"}
                ]
            }
        ))
        
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
    with col3:
        current_disk = server_df['disk_io'].iloc[-1]
        st.metric(label="Disk I/O (%)", value=round(current_disk, 1), 
                 delta=f"{round(current_disk - server_df['disk_io'].iloc[-2], 1)}")
        
        # Disk I/O gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=current_disk,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Disk I/O"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "red"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgreen"},
                    {'range': [50, 80], 'color': "orange"},
                    {'range': [80, 100], 'color': "red"}
                ]
            }
        ))
        
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
    with col4:
        current_network = server_df['network_throughput'].iloc[-1]
        st.metric(label="Network Throughput (Mbps)", value=round(current_network, 1), 
                 delta=f"{round(current_network - server_df['network_throughput'].iloc[-2], 1)}")
        
        # Network gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=current_network,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Network"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "purple"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgreen"},
                    {'range': [50, 80], 'color': "orange"},
                    {'range': [80, 100], 'color': "red"}
                ]
            }
        ))
        
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    
    # Historical trends
    st.subheader("Historical Performance Trends")
    
    # Create historical trend chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=server_df['datetime'],
        y=server_df['cpu_usage'],
        mode='lines',
        name='CPU Usage (%)',
        line=dict(color='blue', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=server_df['datetime'],
        y=server_df['memory_usage'],
        mode='lines',
        name='Memory Usage (%)',
        line=dict(color='green', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=server_df['datetime'],
        y=server_df['disk_io'],
        mode='lines',
        name='Disk I/O (%)',
        line=dict(color='red', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=server_df['datetime'],
        y=server_df['network_throughput'],
        mode='lines',
        name='Network Throughput (Mbps)',
        line=dict(color='purple', width=2)
    ))
    
    fig.update_layout(
        title=f'Historical Performance Metrics for {selected_server}',
        xaxis_title='Time',
        yaxis_title='Value',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Processes Table
    st.subheader("Top Processes")
    
    # Generate sample process data
    process_names = ["httpd", "mysqld", "postgres", "nginx", "python", "java", "sshd", "crond", "systemd", "bash"]
    process_cmds = [
        "/usr/sbin/httpd -DFOREGROUND",
        "/usr/sbin/mysqld --daemonize",
        "/usr/bin/postgres -D /var/lib/postgres/data",
        "/usr/sbin/nginx -g 'daemon off;'",
        "/usr/bin/python3 /app/server.py",
        "/usr/bin/java -jar /app/service.jar",
        "/usr/sbin/sshd -D",
        "/usr/sbin/crond -n",
        "/usr/lib/systemd/systemd --system",
        "/bin/bash"
    ]
    
    process_data = []
    for i in range(10):
        process_data.append({
            "PID": random.randint(1000, 9999),
            "Process": process_names[i],
            "Command": process_cmds[i],
            "CPU (%)": round(random.uniform(0.1, 25.0), 1),
            "Memory (%)": round(random.uniform(0.2, 15.0), 1),
            "Running Time": f"{random.randint(1, 24)}h {random.randint(0, 59)}m"
        })
    
    process_df = pd.DataFrame(process_data).sort_values("CPU (%)", ascending=False)
    
    st.dataframe(process_df, use_container_width=True)

with tab3:
    # Performance Alerts
    st.subheader("Performance Alerts")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        severity_filter = st.multiselect(
            "Filter by Severity",
            options=["Critical", "Warning", "Info"],
            default=["Critical", "Warning"]
        )
        
    with col2:
        status_filter = st.multiselect(
            "Filter by Status",
            options=["Active", "Acknowledged", "Resolved"],
            default=["Active", "Acknowledged"]
        )
        
    with col3:
        resource_filter = st.multiselect(
            "Filter by Resource Type",
            options=["CPU", "Memory", "Disk", "Network"],
            default=["CPU", "Memory", "Disk", "Network"]
        )
    
    # Generate sample alerts
    alert_types = [
        "High CPU Usage",
        "Memory Utilization Threshold Exceeded",
        "Low Disk Space",
        "Disk I/O Bottleneck",
        "Network Interface Saturation",
        "Process Not Responding",
        "Service Restart Required",
        "Memory Leak Detected",
        "Abnormal CPU Spikes",
        "Network Packet Loss"
    ]
    
    resource_map = {
        "High CPU Usage": "CPU",
        "Memory Utilization Threshold Exceeded": "Memory",
        "Low Disk Space": "Disk",
        "Disk I/O Bottleneck": "Disk",
        "Network Interface Saturation": "Network",
        "Process Not Responding": "CPU",
        "Service Restart Required": "CPU",
        "Memory Leak Detected": "Memory",
        "Abnormal CPU Spikes": "CPU",
        "Network Packet Loss": "Network"
    }
    
    alert_data = []
    for i in range(20):
        alert_type = random.choice(alert_types)
        resource_type = resource_map[alert_type]
        severity = random.choice(["Critical", "Warning", "Info"])
        status = random.choice(["Active", "Acknowledged", "Resolved"])
        
        # Only add alerts that match the filters
        if severity in severity_filter and status in status_filter and resource_type in resource_filter:
            timestamp = datetime.datetime.now() - datetime.timedelta(
                hours=random.randint(0, 48),
                minutes=random.randint(0, 59)
            )
            
            server = random.choice(servers)
            
            alert_data.append({
                "Timestamp": timestamp,
                "Server": server,
                "Alert Type": alert_type,
                "Resource": resource_type,
                "Severity": severity,
                "Status": status,
                "Value": f"{random.randint(80, 100)}%" if resource_type in ["CPU", "Memory", "Disk"] else f"{random.randint(50, 100)} Mbps"
            })
    
    if alert_data:
        # Sort by timestamp (most recent first)
        alert_df = pd.DataFrame(alert_data).sort_values("Timestamp", ascending=False)
        
        # Apply styling based on severity and status
        def style_df(row):
            severity = row["Severity"]
            status = row["Status"]
            
            styles = []
            for _ in range(len(row)):
                style = ""
                
                if severity == "Critical":
                    style += "background-color: rgba(255, 0, 0, 0.2);"
                elif severity == "Warning":
                    style += "background-color: rgba(255, 165, 0, 0.2);"
                
                if status == "Resolved":
                    style += "color: gray; text-decoration: line-through;"
                elif status == "Acknowledged":
                    style += "font-style: italic;"
                
                styles.append(style)
            
            return styles
        
        # Apply styling
        styled_alert_df = alert_df.style.apply(style_df, axis=1)
        
        st.dataframe(styled_alert_df, use_container_width=True)
        
        # Download options
        st.download_button(
            label="Export Alerts to CSV",
            data=alert_df.to_csv(index=False).encode("utf-8"),
            file_name=f"performance_alerts_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No alerts match your current filter criteria.")
    
    # Alert trend chart
    st.subheader("Alert Trend Analysis")
    
    # Create sample alert trend data (past 7 days)
    dates = [datetime.datetime.now() - datetime.timedelta(days=i) for i in range(7)]
    dates.reverse()  # Oldest to newest
    
    critical_counts = [random.randint(0, 5) for _ in range(7)]
    warning_counts = [random.randint(3, 12) for _ in range(7)]
    info_counts = [random.randint(5, 20) for _ in range(7)]
    
    trend_df = pd.DataFrame({
        "Date": dates,
        "Critical": critical_counts,
        "Warning": warning_counts,
        "Info": info_counts
    })
    
    # Create the stacked bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=trend_df["Date"],
        y=trend_df["Critical"],
        name="Critical",
        marker_color="red"
    ))
    
    fig.add_trace(go.Bar(
        x=trend_df["Date"],
        y=trend_df["Warning"],
        name="Warning",
        marker_color="orange"
    ))
    
    fig.add_trace(go.Bar(
        x=trend_df["Date"],
        y=trend_df["Info"],
        name="Info",
        marker_color="blue"
    ))
    
    fig.update_layout(
        title="Alert Frequency Trend (Last 7 Days)",
        xaxis_title="Date",
        yaxis_title="Number of Alerts",
        barmode="stack"
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
st.caption("© 2025 - nSocCSP | System Performance Module | Last updated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
