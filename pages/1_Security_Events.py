import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import time
import random
from utils import load_image
from data.mock_generator import generate_security_events

# Page configuration
st.set_page_config(
    page_title="Security Events | nSocCSP",
    page_icon="🔒",
    layout="wide",
)

# Page title
st.title("🔒 Security Event Monitoring")
st.subheader("Real-time monitoring and analysis of security events across your network")

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Event Dashboard", "Event Log", "Event Analytics"])

with tab1:
    # Dashboard view
    st.subheader("Security Event Dashboard")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        event_count = random.randint(100, 500)
        st.metric(label="Total Events (24h)", value=event_count, delta=f"{random.choice([-5, -2, 0, 3, 5, 10])}%")
        
    with col2:
        critical_events = random.randint(5, 20)
        st.metric(label="Critical Events", value=critical_events, delta=f"{random.choice([-2, -1, 0, 1, 2])}")
        
    with col3:
        blocked_attacks = random.randint(50, 150)
        st.metric(label="Blocked Attacks", value=blocked_attacks, delta=f"{random.choice([-4, -2, 0, 3, 5])}")
        
    with col4:
        avg_response = random.randint(2, 10)
        st.metric(label="Avg. Response Time (min)", value=avg_response, delta=f"{random.choice([-2, -1, 0, 1])}")
    
    # Generate security events for the charts
    events = generate_security_events(100)
    events_df = pd.DataFrame(events)
    
    # Format timestamp for better display
    events_df['formatted_time'] = pd.to_datetime(events_df['timestamp']).dt.strftime('%H:%M:%S')
    
    # Event Distribution by Type
    st.subheader("Event Distribution by Type")
    type_dist = events_df['event_type'].value_counts().reset_index()
    type_dist.columns = ['Event Type', 'Count']
    
    fig = px.pie(
        type_dist, 
        values='Count', 
        names='Event Type', 
        title='Security Events by Type',
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Event Severity Timeline
    st.subheader("Event Severity Timeline")
    
    # Ensure the events are sorted by timestamp
    events_df = events_df.sort_values('timestamp')
    
    # Create a severity mapping for numerical values
    severity_map = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
    events_df['severity_num'] = events_df['severity'].map(severity_map)
    
    # Create the scatter plot
    fig = px.scatter(
        events_df,
        x='timestamp',
        y='severity_num',
        color='severity',
        hover_name='event_type',
        hover_data=['source_ip', 'description', 'formatted_time'],
        title='Security Event Severity Timeline',
        color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'},
        labels={'severity_num': 'Severity', 'timestamp': 'Time'}
    )
    
    # Update y-axis to show severity labels
    fig.update_yaxes(
        tickvals=[1, 2, 3, 4],
        ticktext=['Low', 'Medium', 'High', 'Critical']
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Source IP Analysis
    st.subheader("Top Source IPs")
    
    source_counts = events_df['source_ip'].value_counts().nlargest(10).reset_index()
    source_counts.columns = ['Source IP', 'Event Count']
    
    fig = px.bar(
        source_counts,
        x='Source IP',
        y='Event Count',
        color='Event Count',
        color_continuous_scale='Viridis',
        title='Top 10 Source IPs by Event Count'
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Event Log View
    st.subheader("Security Event Log")
    
    # Filtering options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_severity = st.multiselect(
            "Filter by Severity",
            options=['Critical', 'High', 'Medium', 'Low'],
            default=['Critical', 'High']
        )
    
    with col2:
        event_types = list(events_df['event_type'].unique())
        selected_types = st.multiselect(
            "Filter by Event Type",
            options=event_types,
            default=event_types
        )
    
    with col3:
        time_filter = st.selectbox(
            "Time Range",
            options=["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days"]
        )
    
    # Apply filters
    filtered_df = events_df
    
    if selected_severity:
        filtered_df = filtered_df[filtered_df['severity'].isin(selected_severity)]
        
    if selected_types:
        filtered_df = filtered_df[filtered_df['event_type'].isin(selected_types)]
    
    # Add search box
    search_query = st.text_input("Search events (IP, description, ID, etc.)", "")
    
    if search_query:
        # Check if the query is in any of the text columns
        query_mask = filtered_df.apply(
            lambda row: any(
                str(search_query).lower() in str(cell).lower() 
                for cell in row
            ),
            axis=1
        )
        filtered_df = filtered_df[query_mask]
    
    # Display the filtered events table
    if not filtered_df.empty:
        # Format the DataFrame for display
        display_df = filtered_df[['event_id', 'timestamp', 'event_type', 'severity', 'source_ip', 'description']]
        display_df = display_df.sort_values('timestamp', ascending=False)
        
        # Add styling to the dataframe
        def highlight_severity(val):
            if val == 'Critical':
                return 'background-color: darkred; color: white'
            elif val == 'High':
                return 'background-color: red; color: white'
            elif val == 'Medium':
                return 'background-color: orange'
            else:
                return 'background-color: green; color: white'
        
        # Apply the styling
        styled_df = display_df.style.map(
            highlight_severity, 
            subset=['severity']
        )
        
        st.dataframe(styled_df, use_container_width=True)
        
        # Export options
        st.download_button(
            label="Export to CSV",
            data=display_df.to_csv(index=False).encode('utf-8'),
            file_name=f"security_events_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No events match your current filters.")

with tab3:
    # Analytics View
    st.subheader("Security Event Analytics")
    
    # Time-based analysis
    st.markdown("### Event Frequency Analysis")
    
    # Convert timestamp to datetime
    events_df['datetime'] = pd.to_datetime(events_df['timestamp'])
    
    # Extract hour
    events_df['hour'] = events_df['datetime'].dt.hour
    
    # Count events by hour
    hourly_counts = events_df.groupby('hour').size().reset_index(name='count')
    
    # Create the bar chart
    fig = px.bar(
        hourly_counts, 
        x='hour', 
        y='count',
        labels={'hour': 'Hour of Day', 'count': 'Number of Events'},
        title='Event Distribution by Hour of Day',
        color='count',
        color_continuous_scale='Viridis'
    )
    
    fig.update_xaxes(tickmode='linear', tick0=0, dtick=1)
    st.plotly_chart(fig, use_container_width=True)
    
    # Event correlation analysis
    st.markdown("### Event Correlation Analysis")
    
    # Create a heatmap showing correlation between event types and target systems
    if 'target_system' in events_df.columns:
        correlation_df = pd.crosstab(events_df['event_type'], events_df['target_system'])
        
        fig = px.imshow(
            correlation_df,
            labels=dict(x="Target System", y="Event Type", color="Count"),
            title="Correlation between Event Types and Target Systems",
            color_continuous_scale='Viridis'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Target system data not available for correlation analysis.")
    
    # Severity distribution over time
    st.markdown("### Severity Distribution Over Time")
    
    # Extract date for grouping
    events_df['date'] = events_df['datetime'].dt.date
    
    # Create a pivot table with dates and severity
    severity_over_time = pd.pivot_table(
        events_df,
        values='event_id',
        index='date',
        columns='severity',
        aggfunc='count',
        fill_value=0
    ).reset_index()
    
    # Convert back to regular DataFrame format
    severity_over_time = pd.melt(
        severity_over_time,
        id_vars=['date'],
        value_vars=['Low', 'Medium', 'High', 'Critical'],
        var_name='Severity',
        value_name='Count'
    )
    
    # Create the stacked area chart
    fig = px.area(
        severity_over_time,
        x='date',
        y='Count',
        color='Severity',
        title='Severity Distribution Over Time',
        color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'}
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
st.caption("© 2025 - nSocCSP | Security Events Module | Last updated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
