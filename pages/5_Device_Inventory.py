import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import time
import random
from utils import load_image, get_random_ip, get_random_mac
from data.mock_generator import generate_device_inventory

# Set page configuration
st.set_page_config(
    page_title="Device Inventory | nSocCSP",
    page_icon="📋",
    layout="wide"
)

# Page header
st.title("📋 Device Inventory")

# Device Discovery Section
st.subheader("Complete inventory and management of all network devices with status monitoring")
discovery_tab1, discovery_tab2 = st.tabs(["Auto Discovery", "Manual Addition"])

with discovery_tab1:
    discovery_method = st.selectbox(
        "Discovery Method",
        ["LLDP", "CDP", "Mikrotik API", "Cisco SSH", "SNMP"]
    )
    
    if discovery_method in ["Mikrotik API", "Cisco SSH"]:
        col1, col2, col3 = st.columns(3)
        with col1:
            host = st.text_input("Host IP")
        with col2:
            username = st.text_input("Username")
        with col3:
            password = st.text_input("Password", type="password")
    
    elif discovery_method in ["LLDP", "CDP"]:
        interface = st.selectbox("Network Interface", ["eth0", "eth1"])
    
    if st.button("Start Discovery"):
        with st.spinner("Discovering devices..."):
            try:
                discovery = DeviceDiscovery()
                if discovery_method == "LLDP":
                    result = discovery.discover_lldp(interface)
                elif discovery_method == "CDP":
                    result = discovery.discover_cdp(interface)
                elif discovery_method == "Mikrotik API":
                    result = discovery.discover_mikrotik(host, username, password)
                elif discovery_method == "Cisco SSH":
                    result = discovery.discover_cisco(host, username, password)
                
                st.success("Discovery completed!")
                st.json(result)
            except Exception as e:
                st.error(f"Discovery failed: {str(e)}")

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Device List", "Inventory Analysis", "Compliance Status"])

with tab1:
    # Device Inventory List
    st.subheader("Network Device Inventory")
    
    # Generate device inventory data
    devices = generate_device_inventory(50)
    devices_df = pd.DataFrame(devices)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        device_type_filter = st.multiselect(
            "Filter by Device Type",
            options=sorted(list(devices_df['device_type'].unique())),
            default=sorted(list(devices_df['device_type'].unique()))
        )
        
    with col2:
        status_filter = st.multiselect(
            "Filter by Status",
            options=sorted(list(devices_df['status'].unique())),
            default=sorted(list(devices_df['status'].unique()))
        )
        
    with col3:
        network_filter = st.multiselect(
            "Filter by Network",
            options=sorted(list(devices_df['network'].unique())),
            default=sorted(list(devices_df['network'].unique()))
        )
    
    # Add search box
    search_query = st.text_input("Search devices (Name, IP, MAC, Model, etc.)", "")
    
    # Apply filters
    filtered_df = devices_df[
        devices_df['device_type'].isin(device_type_filter) & 
        devices_df['status'].isin(status_filter) & 
        devices_df['network'].isin(network_filter)
    ]
    
    if search_query:
        # Check if the query is in any of the string columns
        query_mask = filtered_df.apply(
            lambda row: any(
                str(search_query).lower() in str(cell).lower() 
                for cell in row
            ),
            axis=1
        )
        filtered_df = filtered_df[query_mask]
    
    # Display the filtered devices table
    if not filtered_df.empty:
        # Format the DataFrame for display
        display_df = filtered_df.copy()
        
        # Add styling to the dataframe
        def highlight_status(val):
            if val == 'online':
                return 'background-color: green; color: white'
            elif val == 'warning':
                return 'background-color: orange; color: white'
            elif val == 'offline':
                return 'background-color: red; color: white'
            elif val == 'maintenance':
                return 'background-color: blue; color: white'
            return ''
        
        # Apply the styling
        styled_df = display_df.style.map(
            highlight_status, 
            subset=['status']
        )
        
        st.dataframe(styled_df, use_container_width=True)
        
        # Export options
        st.download_button(
            label="Export to CSV",
            data=display_df.to_csv(index=False).encode('utf-8'),
            file_name=f"device_inventory_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No devices match your current filters.")
    
    # Device details section
    st.subheader("Device Details")
    
    # Allow user to select a device to view details
    device_ids = list(devices_df['device_id'])
    device_names = list(devices_df['device_name'])
    
    # Create a list of device options (ID + Name)
    device_options = [f"{id} - {name}" for id, name in zip(device_ids, device_names)]
    
    selected_device_option = st.selectbox("Select a device to view details", options=device_options)
    
    if selected_device_option:
        # Extract the device ID from the selected option
        selected_device_id = selected_device_option.split(" - ")[0]
        
        # Find the selected device in the DataFrame
        device_data = devices_df[devices_df['device_id'] == selected_device_id].iloc[0]
        
        # Display device details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### {device_data['device_name']}")
            st.markdown(f"**ID:** {device_data['device_id']}")
            st.markdown(f"**Type:** {device_data['device_type']}")
            st.markdown(f"**Model:** {device_data['model']}")
            st.markdown(f"**Manufacturer:** {device_data['manufacturer']}")
            st.markdown(f"**IP Address:** {device_data['ip_address']}")
            st.markdown(f"**MAC Address:** {device_data['mac_address']}")
            
        with col2:
            status_color = "green" if device_data['status'] == "online" else \
                          "orange" if device_data['status'] == "warning" else \
                          "red" if device_data['status'] == "offline" else "blue"
            
            st.markdown(f"**Status:** <span style='color:{status_color};font-weight:bold'>{device_data['status'].upper()}</span>", unsafe_allow_html=True)
            st.markdown(f"**Network:** {device_data['network']}")
            st.markdown(f"**Location:** {device_data['location']}")
            st.markdown(f"**OS/Firmware:** {device_data['os_version']}")
            st.markdown(f"**Last Updated:** {device_data['last_updated']}")
            
            # Uptime calculation (random for demonstration)
            uptime_days = random.randint(1, 365)
            uptime_hours = random.randint(0, 23)
            uptime_minutes = random.randint(0, 59)
            st.markdown(f"**Uptime:** {uptime_days}d {uptime_hours}h {uptime_minutes}m")
        
        # Performance metrics
        st.markdown("### Device Performance")
        
        # Generate some random performance data for demonstration
        timestamps = pd.date_range(start=datetime.datetime.now() - datetime.timedelta(hours=24), 
                                  end=datetime.datetime.now(), 
                                  freq='h')
        
        cpu_values = [random.randint(10, 90) for _ in range(len(timestamps))]
        memory_values = [random.randint(20, 80) for _ in range(len(timestamps))]
        
        perf_df = pd.DataFrame({
            'Timestamp': timestamps,
            'CPU Usage (%)': cpu_values,
            'Memory Usage (%)': memory_values
        })
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=perf_df['Timestamp'],
            y=perf_df['CPU Usage (%)'],
            mode='lines',
            name='CPU Usage (%)',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=perf_df['Timestamp'],
            y=perf_df['Memory Usage (%)'],
            mode='lines',
            name='Memory Usage (%)',
            line=dict(color='green', width=2)
        ))
        
        fig.update_layout(
            title=f'Performance Metrics for {device_data["device_name"]} (Last 24 Hours)',
            xaxis_title='Time',
            yaxis_title='Usage (%)',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent events
        st.markdown("### Recent Events")
        
        # Generate some random events for demonstration
        event_types = [
            "Login Success", 
            "Configuration Change", 
            "Interface Status Change", 
            "System Restart", 
            "Security Alert"
        ]
        
        event_data = []
        for _ in range(5):
            event_time = datetime.datetime.now() - datetime.timedelta(
                hours=random.randint(0, 24),
                minutes=random.randint(0, 59)
            )
            
            event_type = random.choice(event_types)
            
            if event_type == "Login Success":
                description = f"User 'admin' logged in from {get_random_ip()}"
            elif event_type == "Configuration Change":
                description = f"Configuration changed by user 'admin'"
            elif event_type == "Interface Status Change":
                port = f"GigabitEthernet{random.randint(0, 2)}/{random.randint(0, 24)}"
                status = random.choice(["up", "down"])
                description = f"Interface {port} changed to {status}"
            elif event_type == "System Restart":
                description = "System restarted due to scheduled maintenance"
            else:  # Security Alert
                description = f"Unauthorized access attempt from {get_random_ip()}"
            
            event_data.append({
                "Timestamp": event_time,
                "Event Type": event_type,
                "Description": description
            })
        
        # Sort events by timestamp (most recent first)
        event_df = pd.DataFrame(event_data).sort_values("Timestamp", ascending=False)
        
        st.dataframe(event_df, use_container_width=True)

with tab2:
    # Inventory Analysis
    st.subheader("Inventory Analysis Dashboard")
    
    # Generate stats from the inventory data
    if 'devices_df' in locals():
        # Device Type Distribution
        device_type_counts = devices_df['device_type'].value_counts().reset_index()
        device_type_counts.columns = ['Device Type', 'Count']
        
        # Status Distribution
        status_counts = devices_df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        # Manufacturer Distribution
        manufacturer_counts = devices_df['manufacturer'].value_counts().nlargest(10).reset_index()
        manufacturer_counts.columns = ['Manufacturer', 'Count']
        
        # Network Distribution
        network_counts = devices_df['network'].value_counts().reset_index()
        network_counts.columns = ['Network', 'Count']
        
        # Visualize the distributions
        col1, col2 = st.columns(2)
        
        with col1:
            # Device Type Distribution
            fig = px.pie(
                device_type_counts,
                values='Count',
                names='Device Type',
                title='Device Type Distribution',
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Manufacturer Distribution
            fig = px.bar(
                manufacturer_counts,
                x='Manufacturer',
                y='Count',
                title='Top 10 Manufacturers',
                color='Count',
                color_continuous_scale='Viridis'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            # Status Distribution
            fig = px.pie(
                status_counts,
                values='Count',
                names='Status',
                title='Device Status Distribution',
                color_discrete_map={
                    'online': 'green',
                    'warning': 'orange',
                    'offline': 'red',
                    'maintenance': 'blue'
                }
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Network Distribution
            fig = px.bar(
                network_counts,
                x='Network',
                y='Count',
                title='Device Distribution by Network',
                color='Count',
                color_continuous_scale='Viridis'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # OS/Firmware Analysis
        st.subheader("OS/Firmware Version Analysis")
        
        # Extract OS/Firmware versions
        os_counts = devices_df['os_version'].value_counts().nlargest(10).reset_index()
        os_counts.columns = ['OS/Firmware Version', 'Count']
        
        fig = px.bar(
            os_counts,
            x='OS/Firmware Version',
            y='Count',
            title='Top 10 OS/Firmware Versions',
            color='Count',
            color_continuous_scale='Viridis'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Age Analysis
        st.subheader("Device Age Analysis")
        
        # Add random age data for demonstration
        devices_df['age_months'] = [random.randint(1, 60) for _ in range(len(devices_df))]
        
        # Group by type and calculate average age
        age_by_type = devices_df.groupby('device_type')['age_months'].mean().reset_index()
        age_by_type.columns = ['Device Type', 'Average Age (Months)']
        
        fig = px.bar(
            age_by_type,
            x='Device Type',
            y='Average Age (Months)',
            title='Average Device Age by Type',
            color='Average Age (Months)',
            color_continuous_scale='RdYlGn_r'  # Reversed green-yellow-red scale
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Location Distribution
        st.subheader("Device Location Distribution")
        
        location_counts = devices_df['location'].value_counts().reset_index()
        location_counts.columns = ['Location', 'Count']
        
        fig = px.pie(
            location_counts,
            values='Count',
            names='Location',
            title='Device Distribution by Location',
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No inventory data available for analysis.")

with tab3:
    # Compliance Status
    st.subheader("Device Compliance Status")
    
    # Create compliance data
    if 'devices_df' in locals():
        # Add compliance data to devices
        compliance_categories = [
            "Security Patch Level",
            "Configuration Compliance",
            "Access Control",
            "Encryption Standards",
            "Authentication Methods"
        ]
        
        # Generate compliance scores
        compliance_data = []
        for _, device in devices_df.iterrows():
            device_compliance = {
                "Device ID": device['device_id'],
                "Device Name": device['device_name'],
                "Device Type": device['device_type'],
                "Status": device['status']
            }
            
            # Generate scores for each compliance category
            for category in compliance_categories:
                # Base score on device status (online devices are more likely to be compliant)
                if device['status'] == 'online':
                    score = random.randint(80, 100)
                elif device['status'] == 'warning':
                    score = random.randint(60, 90)
                elif device['status'] == 'maintenance':
                    score = random.randint(50, 95)
                else:  # offline
                    score = random.randint(0, 70)
                
                device_compliance[category] = score
            
            # Calculate overall compliance score
            device_compliance["Overall Score"] = round(
                sum(device_compliance[cat] for cat in compliance_categories) / len(compliance_categories)
            )
            
            compliance_data.append(device_compliance)
        
        compliance_df = pd.DataFrame(compliance_data)
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            compliance_threshold = st.slider(
                "Compliance Threshold (%)", 
                min_value=0, 
                max_value=100, 
                value=70
            )
        
        with col2:
            device_type_filter = st.multiselect(
                "Filter by Device Type",
                options=sorted(list(compliance_df['Device Type'].unique())),
                default=sorted(list(compliance_df['Device Type'].unique())),
                key="compliance_device_type_filter"
            )
        
        # Filter by selected device types and calculate compliance status
        filtered_compliance = compliance_df[compliance_df['Device Type'].isin(device_type_filter)].copy()
        
        # Add compliance status based on threshold
        filtered_compliance['Compliance Status'] = filtered_compliance['Overall Score'].apply(
            lambda x: "Compliant" if x >= compliance_threshold else "Non-Compliant"
        )
        
        # Display compliance status summary
        total_devices = len(filtered_compliance)
        compliant_devices = len(filtered_compliance[filtered_compliance['Compliance Status'] == "Compliant"])
        non_compliant_devices = total_devices - compliant_devices
        compliance_percentage = round((compliant_devices / total_devices) * 100, 1) if total_devices > 0 else 0
        
        st.markdown(f"### Compliance Summary (Threshold: {compliance_threshold}%)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="Total Devices", value=total_devices)
            
        with col2:
            st.metric(label="Compliant Devices", value=compliant_devices)
            
        with col3:
            st.metric(label="Overall Compliance", value=f"{compliance_percentage}%")
        
        # Compliance gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=compliance_percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Compliance Rate"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green"},
                'steps': [
                    {'range': [0, 50], 'color': "red"},
                    {'range': [50, 70], 'color': "orange"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': compliance_threshold
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Compliance by category
        st.subheader("Compliance by Category")
        
        # Calculate average compliance score for each category
        category_scores = {
            category: round(filtered_compliance[category].mean(), 1)
            for category in compliance_categories
        }
        
        category_df = pd.DataFrame({
            'Category': list(category_scores.keys()),
            'Average Score': list(category_scores.values())
        })
        
        fig = px.bar(
            category_df,
            x='Category',
            y='Average Score',
            title='Average Compliance Score by Category',
            color='Average Score',
            color_continuous_scale='RdYlGn',
            range_color=[0, 100]
        )
        
        # Add threshold line
        fig.add_hline(
            y=compliance_threshold,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Threshold ({compliance_threshold}%)",
            annotation_position="bottom right"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Compliance details table
        st.subheader("Device Compliance Details")
        
        # Format table for display
        display_columns = ['Device ID', 'Device Name', 'Device Type', 'Status'] + \
                          compliance_categories + ['Overall Score', 'Compliance Status']
        
        display_compliance = filtered_compliance[display_columns].sort_values('Overall Score', ascending=False)
        
        # Apply styling to the dataframe
        def highlight_compliance(val):
            if val == "Compliant":
                return 'background-color: green; color: white'
            else:
                return 'background-color: red; color: white'
        
        def highlight_score(val):
            if isinstance(val, (int, float)):
                if val >= 90:
                    return 'background-color: rgba(0, 128, 0, 0.2)'
                elif val >= 70:
                    return 'background-color: rgba(255, 255, 0, 0.2)'
                elif val >= 50:
                    return 'background-color: rgba(255, 165, 0, 0.2)'
                else:
                    return 'background-color: rgba(255, 0, 0, 0.2)'
            return ''
        
        # Apply the styling
        styled_compliance = display_compliance.style.map(
            highlight_compliance, 
            subset=['Compliance Status']
        ).map(
            highlight_score,
            subset=compliance_categories + ['Overall Score']
        )
        
        st.dataframe(styled_compliance, use_container_width=True)
        
        # Export options
        st.download_button(
            label="Export Compliance Report to CSV",
            data=display_compliance.to_csv(index=False).encode('utf-8'),
            file_name=f"compliance_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Non-compliant devices focus
        st.subheader("Focus on Non-Compliant Devices")
        
        non_compliant = display_compliance[display_compliance['Compliance Status'] == "Non-Compliant"]
        
        if not non_compliant.empty:
            # Group by device type
            non_compliant_by_type = non_compliant.groupby('Device Type').size().reset_index()
            non_compliant_by_type.columns = ['Device Type', 'Count']
            
            fig = px.pie(
                non_compliant_by_type,
                values='Count',
                names='Device Type',
                title='Non-Compliant Devices by Type',
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Find the most common compliance issues
            issue_counts = {}
            for category in compliance_categories:
                # Count devices that fail this category
                count = len(non_compliant[non_compliant[category] < compliance_threshold])
                issue_counts[category] = count
            
            issue_df = pd.DataFrame({
                'Compliance Category': list(issue_counts.keys()),
                'Non-Compliant Count': list(issue_counts.values())
            }).sort_values('Non-Compliant Count', ascending=False)
            
            fig = px.bar(
                issue_df,
                x='Compliance Category',
                y='Non-Compliant Count',
                title='Most Common Compliance Issues',
                color='Non-Compliant Count',
                color_continuous_scale='Reds'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("All devices meet the compliance threshold!")
    else:
        st.warning("No inventory data available for compliance analysis.")

# Footer
st.divider()
st.caption("© 2025 - nSocCSP | Device Inventory Module | Last updated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
