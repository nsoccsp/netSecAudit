import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import random

def security_summary_card():
    """
    Display a security summary card with key metrics.
    """
    # Generate random metrics for demonstration
    total_events = random.randint(1000, 5000)
    critical_events = random.randint(5, 50)
    high_events = random.randint(50, 200)
    medium_events = random.randint(200, 500)
    low_events = total_events - (critical_events + high_events + medium_events)
    
    with st.container():
        st.subheader("Security Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Events", total_events, f"{random.choice([-5, -2, 0, 3, 5, 10])}%")
            
        with col2:
            st.metric("Critical", critical_events, f"{random.choice([-2, -1, 0, 1, 2])}")
            
        with col3:
            st.metric("High", high_events, f"{random.choice([-5, -3, 0, 2, 4])}")
            
        with col4:
            medium_low = medium_events + low_events
            st.metric("Medium/Low", medium_low, f"{random.choice([-10, -5, 0, 5, 10])}")

def top_alerts_table(num_alerts=5):
    """
    Display a table of top security alerts.
    
    Args:
        num_alerts: Number of alerts to display
    """
    # Generate sample alerts
    alert_types = [
        "Suspicious Login Attempt",
        "Malware Detected",
        "Data Exfiltration Attempt",
        "Port Scanning Activity",
        "Unauthorized Access",
        "Brute Force Attack",
        "Privilege Escalation",
        "DDoS Attack",
        "Ransomware Activity",
        "Configuration Change"
    ]
    
    severities = ["Critical", "High", "Medium", "Low"]
    severity_weights = [0.1, 0.2, 0.4, 0.3]  # Probability distribution
    
    sources = [f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}" for _ in range(5)]
    targets = [f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}" for _ in range(5)]
    
    alerts = []
    for i in range(num_alerts):
        alert_type = random.choice(alert_types)
        severity = random.choices(severities, severity_weights)[0]
        
        timestamp = datetime.datetime.now() - datetime.timedelta(
            minutes=random.randint(1, 60),
            seconds=random.randint(0, 59)
        )
        
        source = random.choice(sources)
        target = random.choice(targets)
        
        alerts.append({
            "timestamp": timestamp,
            "alert_type": alert_type,
            "severity": severity,
            "source": source,
            "target": target
        })
    
    # Create DataFrame and sort by time (most recent first)
    alerts_df = pd.DataFrame(alerts).sort_values("timestamp", ascending=False)
    
    # Apply styling to the dataframe
    def highlight_severity(val):
        if val == "Critical":
            return 'background-color: darkred; color: white'
        elif val == "High":
            return 'background-color: red; color: white'
        elif val == "Medium":
            return 'background-color: orange'
        else:
            return 'background-color: green; color: white'
    
    # Apply the styling
    styled_df = alerts_df.style.map(
        highlight_severity, 
        subset=['severity']
    )
    
    st.subheader("Recent Security Alerts")
    st.dataframe(styled_df, use_container_width=True)

def threat_map():
    """
    Display an interactive threat map.
    """
    st.subheader("Threat Origins Map")
    
    # In a real application, this would be replaced with a map visualization
    # For this example, we'll display a placeholder message
    st.info("Threat map visualization would be displayed here. In a production application, this would show geographic origins of threats using a map visualization library.")
    
    # Example of what would be displayed
    st.markdown("""
    The map would show:
    - Geographic origins of threats
    - Concentration of attack sources
    - Target locations and assets
    - Attack vector paths
    - Real-time threat activity
    """)

def security_metrics_chart():
    """
    Display a chart showing security metrics over time.
    """
    # Generate some sample data
    dates = pd.date_range(start=datetime.datetime.now() - datetime.timedelta(days=30),
                         end=datetime.datetime.now(),
                         freq='D')
    
    data = {
        'date': dates,
        'critical': [random.randint(0, 5) for _ in range(len(dates))],
        'high': [random.randint(3, 15) for _ in range(len(dates))],
        'medium': [random.randint(10, 30) for _ in range(len(dates))],
        'low': [random.randint(20, 50) for _ in range(len(dates))]
    }
    
    df = pd.DataFrame(data)
    
    # Create the stacked area chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['critical'],
        mode='lines',
        name='Critical',
        line=dict(width=0.5, color='darkred'),
        stackgroup='one',
        groupnorm='percent'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['high'],
        mode='lines',
        name='High',
        line=dict(width=0.5, color='red'),
        stackgroup='one'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['medium'],
        mode='lines',
        name='Medium',
        line=dict(width=0.5, color='orange'),
        stackgroup='one'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['low'],
        mode='lines',
        name='Low',
        line=dict(width=0.5, color='green'),
        stackgroup='one'
    ))
    
    fig.update_layout(
        title='Security Incidents by Severity (Last 30 Days)',
        xaxis_title='Date',
        yaxis_title='Percentage',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
