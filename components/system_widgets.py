import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import random

def system_health_gauge(metric_name, value, min_val=0, max_val=100, danger_threshold=80, warning_threshold=60):
    """
    Display a gauge chart for system health metrics.
    
    Args:
        metric_name: Name of the metric (e.g., "CPU Usage")
        value: Current value of the metric
        min_val: Minimum value for the gauge
        max_val: Maximum value for the gauge
        danger_threshold: Threshold for danger zone (red)
        warning_threshold: Threshold for warning zone (yellow)
    """
    # Create the gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': metric_name},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, warning_threshold], 'color': "lightgreen"},
                {'range': [warning_threshold, danger_threshold], 'color': "yellow"},
                {'range': [danger_threshold, max_val], 'color': "salmon"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
    
    st.plotly_chart(fig, use_container_width=True)

def resource_usage_card():
    """
    Display a card with system resource usage metrics.
    """
    st.subheader("System Resource Usage")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cpu_usage = random.randint(20, 80)
        system_health_gauge("CPU Usage (%)", cpu_usage)
        
    with col2:
        memory_usage = random.randint(30, 90)
        system_health_gauge("Memory Usage (%)", memory_usage)
        
    with col3:
        disk_usage = random.randint(40, 95)
        system_health_gauge("Disk Usage (%)", disk_usage)

def system_performance_chart(hours=24):
    """
    Display a chart showing system performance metrics over time.
    
    Args:
        hours: Number of hours of data to display
    """
    st.subheader(f"System Performance (Last {hours} Hours)")
    
    # Generate time series data
    timestamps = pd.date_range(
        start=datetime.datetime.now() - datetime.timedelta(hours=hours),
        end=datetime.datetime.now(),
        freq='15min'
    )
    
    # Generate some random performance data with realistic patterns
    # Use time-of-day patterns to make it realistic
    time_effect = [0.6, 0.5, 0.4, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.8, 0.7, 0.8,  # Hours 0-11
                   0.9, 0.8, 0.7, 0.8, 0.9, 0.8, 0.7, 0.6, 0.7, 0.8, 0.7, 0.6]  # Hours 12-23
    
    cpu_usage = []
    memory_usage = []
    disk_io = []
    
    for ts in timestamps:
        hour_factor = time_effect[ts.hour]
        
        # Add some noise to the pattern
        cpu = 30 + 50 * hour_factor + random.uniform(-10, 10)
        memory = 40 + 40 * hour_factor + random.uniform(-5, 15)
        disk = 20 + 40 * hour_factor + random.uniform(-15, 15)
        
        # Ensure values are within valid ranges
        cpu_usage.append(max(0, min(100, cpu)))
        memory_usage.append(max(0, min(100, memory)))
        disk_io.append(max(0, min(100, disk)))
    
    # Create the DataFrame
    perf_df = pd.DataFrame({
        'timestamp': timestamps,
        'CPU Usage (%)': cpu_usage,
        'Memory Usage (%)': memory_usage,
        'Disk I/O (%)': disk_io
    })
    
    # Create the visualization
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=perf_df['timestamp'],
        y=perf_df['CPU Usage (%)'],
        mode='lines',
        name='CPU Usage (%)',
        line=dict(color='blue', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=perf_df['timestamp'],
        y=perf_df['Memory Usage (%)'],
        mode='lines',
        name='Memory Usage (%)',
        line=dict(color='green', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=perf_df['timestamp'],
        y=perf_df['Disk I/O (%)'],
        mode='lines',
        name='Disk I/O (%)',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Usage (%)',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def process_table(num_processes=10):
    """
    Display a table of top processes by resource usage.
    
    Args:
        num_processes: Number of processes to display
    """
    st.subheader("Top Processes")
    
    # Common process names
    process_names = [
        "httpd", "nginx", "mysqld", "postgres", "java", "python", 
        "node", "chrome", "firefox", "systemd", "sshd", "bash",
        "docker", "containerd", "mongod", "redis-server", "elasticsearch"
    ]
    
    # Generate process data
    processes = []
    for i in range(num_processes):
        process_name = random.choice(process_names)
        pid = random.randint(1000, 9999)
        username = random.choice(["root", "www-data", "mysql", "admin", "app", "system"])
        
        # More realistic resource allocation - processes use different patterns
        if process_name in ["java", "elasticsearch"]:
            # Java processes tend to use more memory
            cpu = random.uniform(1, 15)
            memory = random.uniform(10, 30)
        elif process_name in ["chrome", "firefox"]:
            # Browsers use varied resources
            cpu = random.uniform(5, 25)
            memory = random.uniform(5, 20)
        elif process_name in ["mysqld", "postgres", "mongod"]:
            # Databases are more disk intensive
            cpu = random.uniform(2, 20)
            memory = random.uniform(5, 25)
        else:
            cpu = random.uniform(0.1, 10)
            memory = random.uniform(0.5, 15)
        
        uptime = f"{random.randint(0, 24)}h {random.randint(0, 59)}m"
        
        processes.append({
            "PID": pid,
            "Process": process_name,
            "User": username,
            "CPU (%)": round(cpu, 1),
            "Memory (%)": round(memory, 1),
            "Uptime": uptime
        })
    
    # Sort by CPU usage (highest first)
    processes_df = pd.DataFrame(processes).sort_values("CPU (%)", ascending=False)
    
    # Apply styling based on resource usage
    def highlight_resource_usage(val):
        if isinstance(val, (int, float)):
            if val > 50:
                return 'background-color: rgba(255, 0, 0, 0.2)'
            elif val > 20:
                return 'background-color: rgba(255, 165, 0, 0.2)'
            elif val > 10:
                return 'background-color: rgba(255, 255, 0, 0.1)'
        return ''
    
    # Apply the styling
    styled_df = processes_df.style.map(
        highlight_resource_usage,
        subset=['CPU (%)', 'Memory (%)']
    )
    
    st.dataframe(styled_df, use_container_width=True)

def disk_usage_chart():
    """
    Display a chart showing disk usage by partition.
    """
    st.subheader("Disk Usage by Partition")
    
    # Generate disk partition data
    partitions = ["/", "/home", "/var", "/tmp", "/opt", "/usr"]
    total_sizes = [100, 200, 150, 50, 75, 120]  # in GB
    
    used_percentages = [random.uniform(30, 90) for _ in range(len(partitions))]
    used_sizes = [round(total * pct / 100, 1) for total, pct in zip(total_sizes, used_percentages)]
    free_sizes = [round(total - used, 1) for total, used in zip(total_sizes, used_sizes)]
    
    # Create DataFrame
    disk_df = pd.DataFrame({
        'Partition': partitions,
        'Total (GB)': total_sizes,
        'Used (GB)': used_sizes,
        'Free (GB)': free_sizes,
        'Used (%)': [round(pct, 1) for pct in used_percentages]
    })
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    for i, row in disk_df.iterrows():
        # Determine color based on usage percentage
        if row['Used (%)'] > 80:
            color = 'red'
        elif row['Used (%)'] > 60:
            color = 'orange'
        else:
            color = 'green'
        
        fig.add_trace(go.Bar(
            y=[row['Partition']],
            x=[row['Used (GB)']],
            name=row['Partition'],
            orientation='h',
            marker=dict(color=color),
            text=f"{row['Used (%)']}%",
            textposition='auto',
            hovertemplate=f"<b>{row['Partition']}</b><br>" +
                          f"Used: {row['Used (GB)']} GB ({row['Used (%)']}%)<br>" +
                          f"Free: {row['Free (GB)']} GB<br>" +
                          f"Total: {row['Total (GB)']} GB<extra></extra>"
        ))
    
    fig.update_layout(
        title='Disk Usage by Partition',
        xaxis_title='Used Space (GB)',
        showlegend=False,
        barmode='stack',
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

def system_alerts_widget():
    """
    Display a widget showing recent system alerts.
    """
    st.subheader("Recent System Alerts")
    
    # Generate sample system alerts
    alert_types = [
        "High CPU Usage", 
        "Memory Threshold Exceeded",
        "Disk Space Warning",
        "Service Down",
        "System Reboot Required",
        "High I/O Wait",
        "Network Interface Error",
        "Filesystem Error"
    ]
    
    severities = ["Critical", "Warning", "Info"]
    severity_weights = [0.2, 0.4, 0.4]  # Probability distribution
    
    # Generate random alerts
    alerts = []
    for i in range(5):
        alert_type = random.choice(alert_types)
        severity = random.choices(severities, severity_weights)[0]
        
        # Generate timestamp within last 24 hours
        timestamp = datetime.datetime.now() - datetime.timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Generate descriptive message based on alert type
        if alert_type == "High CPU Usage":
            value = random.randint(80, 100)
            message = f"CPU usage reached {value}% on server"
        elif alert_type == "Memory Threshold Exceeded":
            value = random.randint(85, 100)
            message = f"Memory usage reached {value}% on server"
        elif alert_type == "Disk Space Warning":
            value = random.randint(85, 99)
            partition = random.choice(["/", "/home", "/var"])
            message = f"Disk space at {value}% on {partition} partition"
        elif alert_type == "Service Down":
            service = random.choice(["httpd", "mysqld", "ssh", "nginx"])
            message = f"Service {service} is down"
        elif alert_type == "System Reboot Required":
            days = random.randint(10, 30)
            message = f"System uptime is {days} days, reboot recommended"
        elif alert_type == "High I/O Wait":
            value = random.randint(20, 50)
            message = f"I/O wait at {value}%"
        elif alert_type == "Network Interface Error":
            interface = random.choice(["eth0", "eth1", "bond0"])
            message = f"Errors detected on {interface}"
        else:
            filesystem = random.choice(["/dev/sda1", "/dev/sdb1"])
            message = f"Filesystem errors on {filesystem}"
        
        alerts.append({
            "Timestamp": timestamp,
            "Alert Type": alert_type,
            "Severity": severity,
            "Message": message
        })
    
    # Create DataFrame and sort by timestamp (most recent first)
    alerts_df = pd.DataFrame(alerts).sort_values("Timestamp", ascending=False)
    
    # Apply styling based on severity
    def highlight_severity(val):
        if val == "Critical":
            return 'background-color: red; color: white'
        elif val == "Warning":
            return 'background-color: orange; color: white'
        else:
            return 'background-color: green; color: white'
    
    # Apply the styling
    styled_df = alerts_df.style.map(
        highlight_severity,
        subset=['Severity']
    )
    
    st.dataframe(styled_df, use_container_width=True)
