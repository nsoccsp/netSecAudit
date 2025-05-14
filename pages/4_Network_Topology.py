import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import datetime
import time
import random
from utils import load_image, create_network_graph, get_random_ip, get_random_mac
from data.mock_generator import generate_topology_changes

# Set page configuration
st.set_page_config(
    page_title="Network Topology | nSocCSP",
    page_icon="🌐",
    layout="wide"
)

# Page header
st.title("🌐 Network Topology")
st.subheader("Interactive visualization of your Layer 2 network topology with real-time updates")

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Network Diagram", "Topology Changes", "Topology Analysis"])

with tab1:
    # Network Diagram
    st.subheader("Interactive Network Topology")
    
    # Control panel
    col1, col2, col3 = st.columns(3)
    
    with col1:
        network_size = st.slider("Network Size", min_value=10, max_value=50, value=20, step=5)
        
    with col2:
        edge_count = st.slider("Connection Density", min_value=int(network_size * 0.8), max_value=int(network_size * 2.5), value=int(network_size * 1.5), step=5)
        
    with col3:
        view_type = st.selectbox("View Type", options=["Default", "By Device Type", "By Status"])
    
    # Generate the network graph
    G, pos, edge_x, edge_y, node_x, node_y, node_text, node_size, node_color = create_network_graph(
        num_nodes=network_size,
        num_edges=edge_count
    )
    
    # Create the network diagram
    fig = go.Figure()
    
    # Add edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    ))
    
    # Add nodes
    if view_type == "Default":
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                color=node_color,
                size=node_size,
                line=dict(width=1, color='#333')
            )
        ))
    elif view_type == "By Device Type":
        # Group nodes by device type
        type_groups = {}
        for i, node in enumerate(G.nodes()):
            node_type = G.nodes[node]['type']
            if node_type not in type_groups:
                type_groups[node_type] = {'x': [], 'y': [], 'text': [], 'size': []}
            
            type_groups[node_type]['x'].append(node_x[i])
            type_groups[node_type]['y'].append(node_y[i])
            type_groups[node_type]['text'].append(node_text[i])
            type_groups[node_type]['size'].append(node_size[i])
        
        # Color mapping for device types
        type_colors = {
            'server': 'blue',
            'router': 'red',
            'switch': 'green',
            'client': 'purple'
        }
        
        # Add a trace for each device type
        for node_type, data in type_groups.items():
            fig.add_trace(go.Scatter(
                x=data['x'], y=data['y'],
                mode='markers',
                name=node_type.capitalize(),
                hoverinfo='text',
                text=data['text'],
                marker=dict(
                    color=type_colors.get(node_type, 'gray'),
                    size=data['size'],
                    line=dict(width=1, color='#333')
                )
            ))
    else:  # By Status
        # Group nodes by status
        status_groups = {}
        for i, node in enumerate(G.nodes()):
            node_status = G.nodes[node]['status']
            if node_status not in status_groups:
                status_groups[node_status] = {'x': [], 'y': [], 'text': [], 'size': []}
            
            status_groups[node_status]['x'].append(node_x[i])
            status_groups[node_status]['y'].append(node_y[i])
            status_groups[node_status]['text'].append(node_text[i])
            status_groups[node_status]['size'].append(node_size[i])
        
        # Color mapping for status
        status_colors = {
            'online': 'green',
            'warning': 'orange',
            'offline': 'red'
        }
        
        # Add a trace for each status
        for status, data in status_groups.items():
            fig.add_trace(go.Scatter(
                x=data['x'], y=data['y'],
                mode='markers',
                name=status.capitalize(),
                hoverinfo='text',
                text=data['text'],
                marker=dict(
                    color=status_colors.get(status, 'gray'),
                    size=data['size'],
                    line=dict(width=1, color='#333')
                )
            ))
    
    # Update the layout
    fig.update_layout(
        title='Network Topology Map',
        showlegend=(view_type != "Default"),
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Network statistics
    st.subheader("Network Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total Devices", value=network_size)
        
    with col2:
        st.metric(label="Total Connections", value=edge_count)
        
    with col3:
        # Calculate average connections per device
        avg_connections = round(edge_count / network_size, 1)
        st.metric(label="Avg. Connections Per Device", value=avg_connections)
        
    with col4:
        # Calculate network diameter (longest shortest path)
        try:
            diameter = nx.diameter(G)
            st.metric(label="Network Diameter", value=diameter)
        except nx.NetworkXError:
            st.metric(label="Network Diameter", value="N/A (Disconnected)")
    
    # Network details
    st.subheader("Network Details")
    
    # Count devices by type
    type_counts = {}
    for node in G.nodes():
        node_type = G.nodes[node]['type']
        type_counts[node_type] = type_counts.get(node_type, 0) + 1
    
    type_df = pd.DataFrame({
        'Device Type': list(type_counts.keys()),
        'Count': list(type_counts.values())
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart of device types
        fig = px.pie(
            type_df,
            values='Count',
            names='Device Type',
            title='Device Distribution by Type',
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Status distribution
        status_counts = {}
        for node in G.nodes():
            node_status = G.nodes[node]['status']
            status_counts[node_status] = status_counts.get(node_status, 0) + 1
        
        status_df = pd.DataFrame({
            'Status': list(status_counts.keys()),
            'Count': list(status_counts.values())
        })
        
        fig = px.pie(
            status_df,
            values='Count',
            names='Status',
            title='Device Distribution by Status',
            color_discrete_map={'online': 'green', 'warning': 'orange', 'offline': 'red'}
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Topology Changes
    st.subheader("Recent Topology Changes")
    
    # Generate sample topology changes
    changes = generate_topology_changes(20)
    changes_df = pd.DataFrame(changes).sort_values('timestamp', ascending=False)
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        change_type_filter = st.multiselect(
            "Filter by Change Type",
            options=list(changes_df['change_type'].unique()),
            default=list(changes_df['change_type'].unique())
        )
        
    with col2:
        device_type_filter = st.multiselect(
            "Filter by Device Type",
            options=list(changes_df['device_type'].unique()),
            default=list(changes_df['device_type'].unique())
        )
    
    # Apply filters
    filtered_df = changes_df[
        changes_df['change_type'].isin(change_type_filter) & 
        changes_df['device_type'].isin(device_type_filter)
    ]
    
    # Format the DataFrame for display
    display_df = filtered_df[['timestamp', 'change_type', 'device_id', 'device_type', 'details']]
    
    # Add styling to the dataframe
    def highlight_change_type(val):
        if val == 'Device Added':
            return 'background-color: rgba(0, 128, 0, 0.2)'
        elif val == 'Device Removed':
            return 'background-color: rgba(255, 0, 0, 0.2)'
        elif val == 'Link Added':
            return 'background-color: rgba(0, 0, 255, 0.2)'
        elif val == 'Link Removed':
            return 'background-color: rgba(255, 165, 0, 0.2)'
        elif val == 'Status Change':
            return 'background-color: rgba(128, 0, 128, 0.2)'
        return ''
    
    # Apply the styling
    styled_df = display_df.style.map(
        highlight_change_type, 
        subset=['change_type']
    )
    
    st.dataframe(styled_df, use_container_width=True)
    
    # Change visualization
    st.subheader("Topology Change Trends")
    
    # Group changes by type and date
    changes_df['date'] = pd.to_datetime(changes_df['timestamp']).dt.date
    
    # Count changes by type and date
    change_counts = changes_df.groupby(['date', 'change_type']).size().reset_index(name='count')
    
    # Pivot the data for visualization
    pivot_df = change_counts.pivot(index='date', columns='change_type', values='count').fillna(0)
    pivot_df = pivot_df.reset_index()
    
    # Create a stacked bar chart
    fig = go.Figure()
    
    for change_type in pivot_df.columns[1:]:
        fig.add_trace(go.Bar(
            x=pivot_df['date'],
            y=pivot_df[change_type],
            name=change_type
        ))
    
    fig.update_layout(
        title='Topology Changes Over Time',
        xaxis_title='Date',
        yaxis_title='Number of Changes',
        barmode='stack'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Change impact analysis
    st.subheader("Change Impact Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Impact by device type
        impact_by_device = changes_df.groupby('device_type').size().reset_index(name='count')
        
        fig = px.bar(
            impact_by_device,
            x='device_type',
            y='count',
            title='Changes by Device Type',
            color='count',
            color_continuous_scale='Viridis'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Change type distribution
        change_type_dist = changes_df['change_type'].value_counts().reset_index()
        change_type_dist.columns = ['Change Type', 'Count']
        
        fig = px.pie(
            change_type_dist,
            values='Count',
            names='Change Type',
            title='Distribution of Change Types',
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    # Topology Analysis
    st.subheader("Network Topology Analysis")
    
    # Generate a random network for analysis
    analysis_size = random.randint(50, 100)
    G_analysis = nx.barabasi_albert_graph(analysis_size, 3)  # Scale-free network
    
    # Calculate network metrics
    avg_degree = sum(dict(G_analysis.degree()).values()) / analysis_size
    density = nx.density(G_analysis)
    try:
        avg_clustering = nx.average_clustering(G_analysis)
    except:
        avg_clustering = 0
    
    # Display metrics
    st.markdown("### Network Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Network Size", value=analysis_size)
        
    with col2:
        st.metric(label="Avg. Degree", value=round(avg_degree, 2))
        
    with col3:
        st.metric(label="Network Density", value=round(density, 4))
        
    with col4:
        st.metric(label="Avg. Clustering", value=round(avg_clustering, 4))
    
    # Critical nodes (high betweenness centrality)
    st.markdown("### Critical Nodes Analysis")
    
    # Calculate betweenness centrality
    betweenness = nx.betweenness_centrality(G_analysis)
    
    # Get top 10 nodes by betweenness
    top_nodes = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Create a DataFrame
    node_ids = [n[0] for n in top_nodes]
    centrality = [round(n[1], 4) for n in top_nodes]
    node_types = [random.choice(['router', 'switch', 'server']) for _ in range(10)]
    
    critical_nodes_df = pd.DataFrame({
        'Node ID': node_ids,
        'Device Type': node_types,
        'Betweenness Centrality': centrality,
        'IP Address': [get_random_ip() for _ in range(10)],
        'Status': [random.choice(['online', 'online', 'online', 'warning']) for _ in range(10)]
    })
    
    st.dataframe(critical_nodes_df, use_container_width=True)
    
    # Visualization of centrality
    fig = px.bar(
        critical_nodes_df,
        x='Node ID',
        y='Betweenness Centrality',
        color='Device Type',
        title='Top 10 Critical Nodes (Betweenness Centrality)',
        hover_data=['IP Address', 'Status']
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Vulnerability analysis
    st.markdown("### Network Vulnerability Analysis")
    
    # Generate synthetic vulnerability data
    vulnerability_types = [
        "Single Point of Failure",
        "Bottleneck Link",
        "High Load Node",
        "Redundancy Issue",
        "Connectivity Risk"
    ]
    
    severity_levels = ['Critical', 'High', 'Medium']
    
    vuln_data = []
    for i in range(5):
        vuln_type = vulnerability_types[i]
        severity = severity_levels[random.randint(0, min(i, 2))]
        
        affected_nodes = random.randint(1, 5)
        affected_links = random.randint(0, 3)
        
        risk_score = 0
        if severity == 'Critical':
            risk_score = random.randint(80, 100)
        elif severity == 'High':
            risk_score = random.randint(60, 79)
        else:
            risk_score = random.randint(40, 59)
        
        vuln_data.append({
            'Vulnerability': vuln_type,
            'Severity': severity,
            'Affected Nodes': affected_nodes,
            'Affected Links': affected_links,
            'Risk Score': risk_score,
            'Recommendation': f"Implement {random.choice(['redundancy', 'load balancing', 'failover', 'monitoring'])} for affected components"
        })
    
    vuln_df = pd.DataFrame(vuln_data)
    
    # Apply styling to the dataframe
    def highlight_severity(val):
        if val == 'Critical':
            return 'background-color: red; color: white'
        elif val == 'High':
            return 'background-color: orange; color: white'
        else:
            return 'background-color: yellow'
    
    # Apply the styling
    styled_vuln_df = vuln_df.style.map(
        highlight_severity, 
        subset=['Severity']
    )
    
    st.dataframe(styled_vuln_df, use_container_width=True)
    
    # Risk visualization
    fig = px.scatter(
        vuln_df,
        x='Affected Nodes',
        y='Affected Links',
        size='Risk Score',
        color='Severity',
        hover_name='Vulnerability',
        title='Network Vulnerability Risk Matrix',
        color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow'}
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
st.caption("© 2025 - nSocCSP | Network Topology Module | Last updated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
