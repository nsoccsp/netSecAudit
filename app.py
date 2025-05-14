import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import datetime
import time
import random
import os
import json
from utils import load_image, get_current_phase, get_phase_progress
from data.mock_generator import (
    generate_security_events, 
    generate_system_metrics, 
    get_network_status
)
from database.db_utils import (
    get_session,
    get_security_events,
    get_network_devices,
    get_network_traffic,
    get_device_performance_metrics
)
from sqlalchemy import text

# Load the custom icon
icon = Image.open("generated-icon.png")

# Page configuration
st.set_page_config(
    page_title="nSocCSP",
    page_icon=icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create two columns for the header with custom widths
header_col1, header_col2 = st.columns([1, 10])

with header_col1:
    # Display the image using st.image
    st.image("generated-icon.png", width=100)

with header_col2:
    st.title("CSP - Network and Security Ops Center")

st.subheader("Real-time monitoring and analysis of network security events")

# Get current phase and progress
current_phase, phase_description = get_current_phase()
phase_progress = get_phase_progress()

# Key metrics for dashboard
col1, col2, col3, col4 = st.columns(4)

with col1:
    current_alerts = random.randint(10, 30)
    st.metric(label="Active Alerts", value=current_alerts, delta=f"{random.choice([-2, -1, 1, 2, 3])}")
    
with col2:
    network_devices = random.randint(50, 100)
    st.metric(label="Network Devices", value=network_devices, delta=f"{random.choice([0, 1, 2])}")
    
with col3:
    security_score = random.randint(70, 95)
    st.metric(label="Security Score", value=f"{security_score}%", delta=f"{random.choice([-2, -1, 0, 1, 2])}%")
    
with col4:
    monitored_services = random.randint(15, 25)
    st.metric(label="Monitored Services", value=monitored_services, delta=None)

# Overview sections
st.divider()
st.subheader("Security Overview")

# Recent events
col1, col2 = st.columns([2, 1])

with col1:
    # Generate recent security events
    events = generate_security_events(10)
    events_df = pd.DataFrame(events)
    
    # Chart for event severity
    severity_counts = events_df['severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Count']
    
    fig = px.bar(
        severity_counts, 
        x='Severity', 
        y='Count', 
        color='Severity',
        color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red', 'Critical': 'darkred'},
        title='Recent Events by Severity'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Network status summary
    st.markdown("### Network Status")
    status = get_network_status()
    
    for metric_name, metric_value in status.items():
        if metric_name == "Overall Status":
            status_color = "green" if metric_value == "Healthy" else "orange" if metric_value == "Warning" else "red"
            st.markdown(f"**{metric_name}**: <span style='color:{status_color}'>{metric_value}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"**{metric_name}**: {metric_value}")

# System metrics overview
st.divider()
st.subheader("System Performance")

# Generate system metrics
system_metrics = generate_system_metrics(20)
metrics_df = pd.DataFrame(system_metrics)

# Plot system metrics
fig = go.Figure()
fig.add_trace(go.Scatter(x=metrics_df['timestamp'], y=metrics_df['cpu_usage'], mode='lines', name='CPU Usage'))
fig.add_trace(go.Scatter(x=metrics_df['timestamp'], y=metrics_df['memory_usage'], mode='lines', name='Memory Usage'))
fig.add_trace(go.Scatter(x=metrics_df['timestamp'], y=metrics_df['disk_io'], mode='lines', name='Disk I/O'))
fig.update_layout(title='System Performance Metrics', xaxis_title='Time', yaxis_title='Usage %')

st.plotly_chart(fig, use_container_width=True)

# Project Roadmap
st.divider()
st.subheader("Project Roadmap")

# Phase timeline
phases = [
    {
        "phase": "Phase 1", 
        "name": "Immediate Preparations",
        "description": "Establish an accurate, real-time view of the Layer 2 network.",
        "focus": "Inventory, topology, and documentation.",
        "timeframe": "Weeks 1-2",
        "completed": current_phase > 1,
        "active": current_phase == 1
    },
    {
        "phase": "Phase 2", 
        "name": "Monitoring Deployment",
        "description": "Gain visibility into traffic behavior, port performance, and topology changes.",
        "focus": "SNMP/sFlow, alerting, STP tracking.",
        "timeframe": "Weeks 3-6",
        "completed": current_phase > 2,
        "active": current_phase == 2
    },
    {
        "phase": "Phase 3", 
        "name": "Auditing and Policy Checks",
        "description": "Harden infrastructure against misconfigurations and internal threats.",
        "focus": "VLAN correctness, rogue devices, loop control.",
        "timeframe": "Weeks 7-10",
        "completed": current_phase > 3,
        "active": current_phase == 3
    },
    {
        "phase": "Ongoing", 
        "name": "Monitoring and Maintenance",
        "description": "Continuous monitoring and improvement of network security.",
        "focus": "Regular audits, updates, and optimizations.",
        "timeframe": "After Week 10",
        "completed": False,
        "active": current_phase > 3
    }
]

# Display roadmap
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown(f"**Current Phase:** Phase {current_phase}")
    st.markdown(f"**Focus:** {phase_description}")
    st.progress(phase_progress)

with col2:
    for phase in phases:
        if phase["completed"]:
            status_icon = "✅"
            status_color = "green"
        elif phase["active"]:
            status_icon = "🔄"
            status_color = "orange"
        else:
            status_icon = "⏳"
            status_color = "gray"
            
        st.markdown(
            f"{status_icon} **{phase['phase']} - {phase['name']}** ({phase['timeframe']})\n\n"
            f"<span style='color:{status_color}'>{phase['description']}</span>\n\n"
            f"Focus: {phase['focus']}",
            unsafe_allow_html=True
        )

# Footer
st.divider()
st.caption("© 2025 - nSocCSP | Last updated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
