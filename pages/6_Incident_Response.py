import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import random
import nmap
import io
import base64
from scapy.all import IP, TCP, ICMP, UDP, rdpcap
from sqlalchemy import text
import textwrap
from database.db_utils import get_session
from database.models import SecurityEvent, AlertSeverity

# Set page configuration
st.set_page_config(
    page_title="Incident Response | nSocCSP",
    page_icon="🚨",
    layout="wide"
)

# Page header
st.title("🚨 Incident Response")
st.subheader("Manage and respond to security incidents")

# Incident Management Tabs
tabs = st.tabs(["Active Incidents", "Incident Details", "Playbooks", "Forensics", "Real-time Response"])

# Helper functions
def get_incident_status_color(status):
    colors = {
        "New": "red",
        "In Progress": "orange",
        "Contained": "blue",
        "Resolved": "green",
        "Closed": "gray"
    }
    return colors.get(status, "gray")

def time_since(timestamp):
    now = datetime.datetime.now()
    delta = now - timestamp
    
    if delta.days > 0:
        return f"{delta.days} days ago"
    elif delta.seconds >= 3600:
        return f"{delta.seconds // 3600} hours ago"
    elif delta.seconds >= 60:
        return f"{delta.seconds // 60} minutes ago"
    else:
        return f"{delta.seconds} seconds ago"

def get_security_events():
    # Get data from the database
    session = get_session()
    try:
        query = text("""
            SELECT 
                se.id, 
                se.timestamp, 
                se.event_type, 
                se.source_ip, 
                se.destination_ip,
                se.description, 
                se.severity, 
                se.is_resolved,
                nd.device_name
            FROM security_events se
            LEFT JOIN network_devices nd ON se.device_id = nd.id
            ORDER BY se.timestamp DESC
        """)
        
        result = session.execute(query)
        
        events = []
        for row in result:
            # Convert to a dictionary for easier handling
            event = {
                "id": row[0],
                "timestamp": row[1],
                "event_type": row[2],
                "source_ip": row[3],
                "destination_ip": row[4],
                "description": row[5],
                "severity": row[6].lower() if row[6] else "unknown",
                "is_resolved": row[7],
                "device_name": row[8] if row[8] else "Unknown Device"
            }
            events.append(event)
            
        return events
    except Exception as e:
        st.error(f"Error retrieving security events: {str(e)}")
        return []
    finally:
        session.close()

# Load sample incident data or create if not exists
if 'incidents' not in st.session_state:
    # Create some sample incidents based on security events
    events = get_security_events()
    
    incidents = []
    incident_types = ["Malware", "Unauthorized Access", "Data Breach", "DoS Attack", "Phishing"]
    statuses = ["New", "In Progress", "Contained", "Resolved", "Closed"]
    weights = [0.3, 0.3, 0.2, 0.1, 0.1]  # More likely to be new or in progress
    
    # Create incidents from the most severe security events
    for i, event in enumerate(events[:10]):  # Take top 10 events
        severity = event["severity"].lower()
        if severity in ["high", "critical"]:
            incident_id = f"INC-{random.randint(10000, 99999)}"
            
            # Make most incidents new or in progress for demo
            status = random.choices(statuses, weights=weights)[0]
            
            # Create an incident record
            incident = {
                "id": incident_id,
                "title": f"{event['event_type']} - {event['device_name']}",
                "type": random.choice(incident_types),
                "severity": severity,
                "status": status,
                "detected": event["timestamp"],
                "updated": datetime.datetime.now() - datetime.timedelta(hours=random.randint(0, 24)),
                "affected_systems": [event["device_name"]],
                "source_ip": event["source_ip"],
                "description": event["description"],
                "assigned_to": f"user{random.randint(1, 5)}@example.com",
                "related_events": [event["id"]],
                "timeline": [
                    {
                        "timestamp": event["timestamp"],
                        "action": "Incident detected",
                        "user": "system"
                    }
                ],
                "notes": []
            }
            
            # Add some timeline entries for older incidents
            if status != "New":
                # Add assignment
                assignment_time = event["timestamp"] + datetime.timedelta(minutes=random.randint(5, 30))
                incident["timeline"].append({
                    "timestamp": assignment_time,
                    "action": f"Incident assigned to {incident['assigned_to']}",
                    "user": "system"
                })
                
                # Add investigation
                if status not in ["New"]:
                    investigation_time = assignment_time + datetime.timedelta(minutes=random.randint(15, 60))
                    incident["timeline"].append({
                        "timestamp": investigation_time,
                        "action": "Investigation started",
                        "user": incident['assigned_to']
                    })
                
                # Add containment
                if status in ["Contained", "Resolved", "Closed"]:
                    containment_time = investigation_time + datetime.timedelta(hours=random.randint(1, 4))
                    incident["timeline"].append({
                        "timestamp": containment_time,
                        "action": "Threat contained",
                        "user": incident['assigned_to']
                    })
                
                # Add resolution
                if status in ["Resolved", "Closed"]:
                    resolution_time = containment_time + datetime.timedelta(hours=random.randint(2, 8))
                    incident["timeline"].append({
                        "timestamp": resolution_time,
                        "action": "Incident resolved",
                        "user": incident['assigned_to']
                    })
                    
                    # Add some notes
                    incident["notes"].append({
                        "timestamp": resolution_time - datetime.timedelta(minutes=30),
                        "user": incident['assigned_to'],
                        "text": f"Root cause identified: {random.choice(['Outdated software', 'Weak credentials', 'Misconfiguration', 'Zero-day vulnerability'])}"
                    })
                
                # Add closure
                if status == "Closed":
                    closure_time = resolution_time + datetime.timedelta(days=random.randint(1, 3))
                    incident["timeline"].append({
                        "timestamp": closure_time,
                        "action": "Incident closed",
                        "user": "supervisor@example.com"
                    })
            
            incidents.append(incident)
    
    if not incidents:
        # Create at least one sample incident if no events were suitable
        incidents = [{
            "id": "INC-10001",
            "title": "Suspected Malware Activity",
            "type": "Malware",
            "severity": "high",
            "status": "New",
            "detected": datetime.datetime.now() - datetime.timedelta(hours=2),
            "updated": datetime.datetime.now() - datetime.timedelta(hours=1),
            "affected_systems": ["web-server-001"],
            "source_ip": "192.168.1.100",
            "description": "Unusual process activity detected on web server",
            "assigned_to": "security@example.com",
            "related_events": [1, 2, 3],
            "timeline": [
                {
                    "timestamp": datetime.datetime.now() - datetime.timedelta(hours=2),
                    "action": "Incident detected",
                    "user": "system"
                }
            ],
            "notes": []
        }]
    
    st.session_state.incidents = incidents

# ACTIVE INCIDENTS TAB
with tabs[0]:
    st.markdown("### Incident Summary")
    
    # Create incident metrics
    incidents = st.session_state.incidents
    total_incidents = len(incidents)
    open_incidents = len([i for i in incidents if i["status"] not in ["Resolved", "Closed"]])
    critical_incidents = len([i for i in incidents if i["severity"] == "critical" and i["status"] not in ["Resolved", "Closed"]])
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Incidents", total_incidents)
    col2.metric("Open Incidents", open_incidents)
    col3.metric("Critical/High", critical_incidents)
    col4.metric("MTT Resolution", "4.2 hours")
    
    # Filters
    st.markdown("### Active Incidents")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        status_filter = st.multiselect(
            "Status",
            options=["New", "In Progress", "Contained", "Resolved", "Closed"],
            default=["New", "In Progress", "Contained"],
            key="incident_status_filter"
        )
    
    with filter_col2:
        severity_filter = st.multiselect(
            "Severity",
            options=["Critical", "High", "Medium", "Low"],
            default=["Critical", "High"],
            key="incident_severity_filter"
        )
    
    with filter_col3:
        type_filter = st.multiselect(
            "Incident Type",
            options=["Malware", "Unauthorized Access", "Data Breach", "DoS Attack", "Phishing"],
            default=[],
            key="incident_type_filter"
        )
    
    # Filter incidents
    filtered_incidents = incidents
    if status_filter:
        filtered_incidents = [i for i in filtered_incidents if i["status"] in status_filter]
    if severity_filter:
        filtered_incidents = [i for i in filtered_incidents if i["severity"].capitalize() in severity_filter]
    if type_filter:
        filtered_incidents = [i for i in filtered_incidents if i["type"] in type_filter]
    
    # Create incident table
    if filtered_incidents:
        incident_df = pd.DataFrame([
            {
                "ID": i["id"],
                "Title": i["title"],
                "Type": i["type"],
                "Severity": i["severity"].capitalize(),
                "Status": i["status"],
                "Detected": i["detected"],
                "Age": time_since(i["detected"]),
                "Assigned To": i["assigned_to"]
            } for i in filtered_incidents
        ])
        
        # Style the dataframe
        def highlight_severity(val):
            if val == "Critical":
                return 'background-color: red; color: white'
            elif val == "High":
                return 'background-color: orange; color: white'
            elif val == "Medium":
                return 'background-color: yellow; color: black'
            else:
                return 'background-color: green; color: white'
        
        def highlight_status(val):
            color = get_incident_status_color(val)
            return f'background-color: {color}; color: white'
        
        styled_df = incident_df.style.map(
            highlight_severity, 
            subset=['Severity']
        ).map(
            highlight_status,
            subset=['Status']
        )
        
        st.dataframe(styled_df, use_container_width=True)
        
        # Create a selection box for incident details
        selected_incident_id = st.selectbox(
            "Select an incident to view details",
            options=incident_df["ID"].tolist(),
            key="selected_incident"
        )
        
        if st.button("View Selected Incident Details"):
            st.session_state.active_incident = selected_incident_id
            st.rerun()
    else:
        st.info("No incidents match the selected filters.")

# INCIDENT DETAILS TAB
with tabs[1]:
    # Show incident details if one is selected
    if hasattr(st.session_state, 'active_incident') and st.session_state.active_incident:
        incident_id = st.session_state.active_incident
        incident = next((i for i in st.session_state.incidents if i["id"] == incident_id), None)
        
        if incident:
            # Header with key details
            st.markdown(f"### {incident['title']} ({incident['id']})")
            
            status_color = get_incident_status_color(incident["status"])
            severity_color = "red" if incident["severity"] == "critical" else "orange" if incident["severity"] == "high" else "yellow" if incident["severity"] == "medium" else "green"
            
            st.markdown(f"""
            <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                <span style="background-color: {status_color}; color: white; padding: 5px 10px; border-radius: 5px;">Status: {incident["status"]}</span>
                <span style="background-color: {severity_color}; color: black; padding: 5px 10px; border-radius: 5px;">Severity: {incident["severity"].capitalize()}</span>
                <span style="background-color: #444; color: white; padding: 5px 10px; border-radius: 5px;">Assigned: {incident["assigned_to"]}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Incident details
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Incident Information")
                st.markdown(f"**Type:** {incident['type']}")
                st.markdown(f"**Detected:** {incident['detected'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**Last Updated:** {incident['updated'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**Source IP:** {incident['source_ip']}")
                st.markdown(f"**Affected Systems:** {', '.join(incident['affected_systems'])}")
                
                # Update status
                st.markdown("#### Update Status")
                new_status = st.selectbox(
                    "Change Status",
                    options=["New", "In Progress", "Contained", "Resolved", "Closed"],
                    index=["New", "In Progress", "Contained", "Resolved", "Closed"].index(incident["status"]),
                    key="new_status"
                )
                
                new_assignee = st.text_input("Reassign To", value=incident["assigned_to"], key="new_assignee")
                
                if st.button("Update Incident"):
                    old_status = incident["status"]
                    if new_status != old_status:
                        # Add to timeline
                        incident["timeline"].append({
                            "timestamp": datetime.datetime.now(),
                            "action": f"Status changed from {old_status} to {new_status}",
                            "user": "current_user@example.com"
                        })
                        incident["status"] = new_status
                        incident["updated"] = datetime.datetime.now()
                    
                    old_assignee = incident["assigned_to"]
                    if new_assignee != old_assignee:
                        # Add to timeline
                        incident["timeline"].append({
                            "timestamp": datetime.datetime.now(),
                            "action": f"Reassigned from {old_assignee} to {new_assignee}",
                            "user": "current_user@example.com"
                        })
                        incident["assigned_to"] = new_assignee
                        incident["updated"] = datetime.datetime.now()
                    
                    st.success("Incident updated successfully")
            
            with col2:
                st.markdown("#### Description")
                st.text_area("Incident Description", incident["description"], height=100, disabled=True)
                
                st.markdown("#### Add Note")
                new_note = st.text_area("New Note", "", height=100, key="new_note")
                
                if st.button("Add Note"):
                    if new_note:
                        incident["notes"].append({
                            "timestamp": datetime.datetime.now(),
                            "user": "current_user@example.com",
                            "text": new_note
                        })
                        incident["updated"] = datetime.datetime.now()
                        st.success("Note added successfully")
                        st.rerun()
                    else:
                        st.warning("Please enter a note")
            
            # Timeline and activity
            st.markdown("#### Timeline")
            
            # Sort timeline events by timestamp
            timeline_events = sorted(incident["timeline"], key=lambda x: x["timestamp"], reverse=True)
            
            # Create a dataframe for the timeline
            timeline_df = pd.DataFrame([
                {
                    "Time": event["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                    "User": event["user"],
                    "Action": event["action"]
                } for event in timeline_events
            ])
            
            st.dataframe(timeline_df, use_container_width=True)
            
            # Notes section
            if incident["notes"]:
                st.markdown("#### Notes")
                notes = sorted(incident["notes"], key=lambda x: x["timestamp"], reverse=True)
                
                for note in notes:
                    st.markdown(f"""
                    <div style="border-left: 3px solid #ccc; padding-left: 10px; margin-bottom: 10px;">
                        <p style="margin-bottom: 5px;"><strong>{note["user"]}</strong> - {note["timestamp"].strftime("%Y-%m-%d %H:%M:%S")}</p>
                        <p style="margin-top: 0;">{note["text"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Related events
            st.markdown("#### Related Security Events")
            events = get_security_events()
            related_events = [e for e in events if e["id"] in incident["related_events"]]
            
            if related_events:
                related_df = pd.DataFrame([
                    {
                        "ID": event["id"],
                        "Time": event["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                        "Type": event["event_type"],
                        "Source IP": event["source_ip"],
                        "Severity": event["severity"].capitalize(),
                        "Description": textwrap.shorten(event["description"], width=50, placeholder="...")
                    } for event in related_events
                ])
                
                st.dataframe(related_df, use_container_width=True)
            else:
                st.info("No related events found")
            
            # Evidence and artifacts
            st.markdown("#### Evidence Collection")
            
            evidence_col1, evidence_col2 = st.columns(2)
            
            with evidence_col1:
                st.file_uploader("Upload Evidence Files", accept_multiple_files=True, key="evidence_upload")
            
            with evidence_col2:
                st.text_input("Evidence Description", placeholder="Describe the uploaded evidence", key="evidence_description")
            
            if st.button("Attach Evidence"):
                st.success("Evidence would be attached to the incident (demo)")
        else:
            st.info("Select an incident from the Active Incidents tab to view details.")
    else:
        st.info("Select an incident from the Active Incidents tab to view details.")

# PLAYBOOKS TAB
with tabs[2]:
    st.markdown("### Incident Response Playbooks")
    st.caption("Standardized procedures for handling different types of security incidents")
    
    # Playbook selection
    playbook_options = {
        "Malware Response": {
            "steps": ["Isolate affected systems", "Identify malware type", "Remove malware", "Restore from backup", "Update antivirus signatures"],
            "description": "Procedure for handling malware infections"
        },
        "Data Breach": {
            "steps": ["Identify compromised data", "Contain the breach", "Assess impact", "Notify affected parties", "Remediate vulnerabilities"],
            "description": "Response to unauthorized data access incidents"
        },
        "Ransomware": {
            "steps": ["Isolate affected systems", "Preserve evidence", "Determine encryption type", "Assess backup viability", "Containment and eradication"],
            "description": "Procedure for ransomware attacks"
        },
        "Phishing Attack": {
            "steps": ["Analyze phishing message", "Block sender", "Check for compromised accounts", "Reset passwords", "Scan for malware"],
            "description": "Response to phishing attempts"
        },
        "Unauthorized Access": {
            "steps": ["Terminate unauthorized sessions", "Reset credentials", "Identify access vector", "Review logs", "Implement additional controls"],
            "description": "Handling unauthorized system access"
        }
    }
    
    selected_playbook = st.selectbox(
        "Select Playbook",
        options=list(playbook_options.keys()),
        key="playbook_selector"
    )
    
    if selected_playbook:
        playbook = playbook_options[selected_playbook]
        
        st.markdown(f"#### {selected_playbook} Playbook")
        st.markdown(f"*{playbook['description']}*")
        
        st.markdown("#### Response Procedure")
        
        for i, step in enumerate(playbook["steps"], 1):
            st.checkbox(f"{i}. {step}", key=f"step_{i}")
        
        # Playbook execution tracking
        st.markdown("#### Playbook Execution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if hasattr(st.session_state, 'active_incident') and st.session_state.active_incident:
                st.text_input("Incident ID", value=st.session_state.active_incident, disabled=True)
            else:
                st.text_input("Incident ID", placeholder="Enter incident ID")
        
        with col2:
            st.text_input("Assigned To", placeholder="Enter assignee email")
        
        st.text_area("Notes", placeholder="Enter execution notes", height=100)
        
        if st.button("Start Playbook Execution"):
            st.success(f"{selected_playbook} playbook execution started")

# FORENSICS TAB
with tabs[3]:
    st.markdown("### Digital Forensics Tools")
    st.caption("Tools for collecting and analyzing forensic evidence")
    
    # Tool selection
    forensic_tool_options = ["Network Packet Analysis", "Memory Dump Analysis", "Log Analysis", "Disk Forensics"]
    selected_tool = st.radio("Select Forensic Tool", options=forensic_tool_options)
    
    if selected_tool == "Network Packet Analysis":
        st.markdown("#### Network Packet Analysis")
        
        st.file_uploader("Upload PCAP File", type=["pcap", "pcapng"], key="pcap_upload")
        
        # Sample PCAP analysis (simulated since we can't read uploaded files directly)
        if st.button("Analyze Sample Data"):
            st.info("Simulating packet analysis on sample PCAP data")
            
            # Simulated packet data
            packet_types = ["TCP", "UDP", "ICMP", "HTTP", "DNS", "HTTPS"]
            timestamps = [datetime.datetime.now() - datetime.timedelta(minutes=i*5) for i in range(20)]
            
            packets = []
            for i in range(20):
                packet_type = random.choice(packet_types)
                src_ip = f"192.168.1.{random.randint(1, 254)}"
                dst_ip = f"192.168.2.{random.randint(1, 254)}"
                
                packet = {
                    "timestamp": timestamps[i],
                    "type": packet_type,
                    "src_ip": src_ip,
                    "dst_ip": dst_ip,
                    "size": random.randint(64, 1500),
                    "info": f"Sample {packet_type} packet"
                }
                packets.append(packet)
            
            packets_df = pd.DataFrame(packets)
            
            # Display packet summary
            st.markdown("#### Packet Summary")
            st.dataframe(packets_df, use_container_width=True)
            
            # Display packet type distribution
            st.markdown("#### Packet Type Distribution")
            fig = px.pie(packets_df, names="type", title="Packet Types")
            st.plotly_chart(fig, use_container_width=True)
            
            # Display communication graph
            st.markdown("#### Communication Graph")
            st.info("Communication graph would be displayed here")
            
            # Anomaly detection
            st.markdown("#### Anomaly Detection")
            st.success("No network anomalies detected in the sample data")
    
    elif selected_tool == "Memory Dump Analysis":
        st.markdown("#### Memory Dump Analysis")
        st.file_uploader("Upload Memory Dump", type=["dmp", "raw", "mem"], key="memory_upload")
        
        analyze_options = ["Process List", "Network Connections", "Registry Hives", "Loaded DLLs"]
        
        selected_analysis = st.multiselect(
            "Select Analysis Types",
            options=analyze_options,
            default=["Process List", "Network Connections"]
        )
        
        if st.button("Analyze Memory (Demo)"):
            st.info("Memory analysis would be performed here (demonstration only)")
            
            # Sample process list
            if "Process List" in selected_analysis:
                st.markdown("#### Process List")
                
                processes = [
                    {"PID": 4, "Name": "System", "Path": "N/A", "Started": "System startup", "User": "SYSTEM"},
                    {"PID": 504, "Name": "lsass.exe", "Path": "C:\\Windows\\System32\\", "Started": "System startup", "User": "SYSTEM"},
                    {"PID": 324, "Name": "svchost.exe", "Path": "C:\\Windows\\System32\\", "Started": "System startup", "User": "SYSTEM"},
                    {"PID": 1876, "Name": "explorer.exe", "Path": "C:\\Windows\\", "Started": "User login", "User": "user1"},
                    {"PID": 2456, "Name": "chrome.exe", "Path": "C:\\Program Files\\Google\\Chrome\\", "Started": "10:15:34", "User": "user1"},
                    {"PID": 3012, "Name": "malware.exe", "Path": "C:\\Temp\\", "Started": "10:32:12", "User": "user1"}
                ]
                
                processes_df = pd.DataFrame(processes)
                st.dataframe(processes_df, use_container_width=True)
                
                # Highlight suspicious process
                st.warning("Suspicious process detected: malware.exe")
            
            # Sample network connections
            if "Network Connections" in selected_analysis:
                st.markdown("#### Active Network Connections")
                
                connections = [
                    {"Local Address": "192.168.1.100:3389", "Remote Address": "192.168.1.200:52134", "State": "ESTABLISHED", "PID": 504, "Process": "lsass.exe"},
                    {"Local Address": "192.168.1.100:445", "Remote Address": "192.168.1.50:60123", "State": "ESTABLISHED", "PID": 4, "Process": "System"},
                    {"Local Address": "192.168.1.100:50123", "Remote Address": "8.8.8.8:53", "State": "ESTABLISHED", "PID": 2456, "Process": "chrome.exe"},
                    {"Local Address": "192.168.1.100:50124", "Remote Address": "209.85.167.188:443", "State": "ESTABLISHED", "PID": 2456, "Process": "chrome.exe"},
                    {"Local Address": "192.168.1.100:50125", "Remote Address": "185.159.131.12:443", "State": "ESTABLISHED", "PID": 3012, "Process": "malware.exe"}
                ]
                
                connections_df = pd.DataFrame(connections)
                st.dataframe(connections_df, use_container_width=True)
                
                # Highlight suspicious connection
                st.warning("Suspicious connection detected from malware.exe to 185.159.131.12:443")
    
    elif selected_tool == "Log Analysis":
        st.markdown("#### Log Analysis")
        
        log_type = st.selectbox(
            "Log Type",
            options=["Windows Event Logs", "Firewall Logs", "Web Server Logs", "Authentication Logs", "Custom Log Format"]
        )
        
        st.file_uploader("Upload Log File", type=["log", "evt", "evtx", "txt", "csv"], key="log_upload")
        
        log_options = st.expander("Log Analysis Options")
        with log_options:
            st.checkbox("Extract timestamps", value=True)
            st.checkbox("Identify authentication failures", value=True)
            st.checkbox("Detect privilege escalation", value=True)
            st.checkbox("Find unusual access patterns", value=True)
            st.checkbox("Generate timeline", value=True)
        
        if st.button("Analyze Logs (Demo)"):
            st.info("Log analysis would be performed here (demonstration)")
            
            # Sample log entries
            st.markdown("#### Sample Log Analysis Results")
            
            log_entries = [
                {"Timestamp": "2023-04-15 08:32:45", "Event ID": 4625, "Type": "Authentication Failure", "User": "admin", "Source": "192.168.1.50", "Description": "Failed login attempt"},
                {"Timestamp": "2023-04-15 08:33:12", "Event ID": 4625, "Type": "Authentication Failure", "User": "admin", "Source": "192.168.1.50", "Description": "Failed login attempt"},
                {"Timestamp": "2023-04-15 08:33:45", "Event ID": 4625, "Type": "Authentication Failure", "User": "admin", "Source": "192.168.1.50", "Description": "Failed login attempt"},
                {"Timestamp": "2023-04-15 08:34:23", "Event ID": 4624, "Type": "Authentication Success", "User": "admin", "Source": "192.168.1.50", "Description": "Successful login"},
                {"Timestamp": "2023-04-15 08:35:11", "Event ID": 4672, "Type": "Privilege Assignment", "User": "admin", "Source": "192.168.1.50", "Description": "Administrator privileges assigned"},
                {"Timestamp": "2023-04-15 08:36:45", "Event ID": 7045, "Type": "Service Installation", "User": "admin", "Source": "SYSTEM", "Description": "New service installed: RemoteAccess"}
            ]
            
            log_df = pd.DataFrame(log_entries)
            st.dataframe(log_df, use_container_width=True)
            
            # Identified alerts
            st.markdown("#### Identified Alerts")
            st.warning("Multiple failed login attempts detected for 'admin' account")
            st.warning("Privilege escalation activity detected")
            st.warning("New service installation - potential persistence mechanism")
            
            # Timeline
            st.markdown("#### Activity Timeline")
            
            fig = px.timeline(
                log_df, 
                x_start="Timestamp", 
                x_end="Timestamp", 
                y="Type", 
                color="Type",
                hover_data=["User", "Source", "Description"]
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif selected_tool == "Disk Forensics":
        st.markdown("#### Disk Forensics")
        st.caption("Analyze disk images for evidence")
        
        st.file_uploader("Upload Disk Image", type=["dd", "raw", "img", "001"], key="disk_upload")
        
        analysis_options = ["File System Analysis", "Deleted File Recovery", "String Search", "Timeline Creation"]
        
        selected_analysis = st.multiselect(
            "Select Analysis Types",
            options=analysis_options,
            default=["File System Analysis"]
        )
        
        # Search options
        search_term = st.text_input("Search for specific strings or patterns")
        
        if st.button("Perform Analysis (Demo)"):
            st.info("Disk forensics would be performed here (demonstration)")
            
            # Sample results
            if "File System Analysis" in selected_analysis:
                st.markdown("#### File System Analysis Results")
                
                files = [
                    {"Path": "C:\\Windows\\System32\\cmd.exe", "Size": "219 KB", "Created": "2023-01-15 08:32:45", "Modified": "2023-01-15 08:32:45", "Accessed": "2023-04-15 08:36:12", "Owner": "SYSTEM"},
                    {"Path": "C:\\Windows\\System32\\rundll32.exe", "Size": "33 KB", "Created": "2023-01-15 08:32:45", "Modified": "2023-01-15 08:32:45", "Accessed": "2023-04-15 08:35:42", "Owner": "SYSTEM"},
                    {"Path": "C:\\Temp\\data.zip", "Size": "4.2 MB", "Created": "2023-04-15 08:40:12", "Modified": "2023-04-15 08:40:12", "Accessed": "2023-04-15 08:40:12", "Owner": "admin"},
                    {"Path": "C:\\Temp\\exfil.ps1", "Size": "2.3 KB", "Created": "2023-04-15 08:38:45", "Modified": "2023-04-15 08:38:45", "Accessed": "2023-04-15 08:42:10", "Owner": "admin"}
                ]
                
                files_df = pd.DataFrame(files)
                st.dataframe(files_df, use_container_width=True)
                
                st.warning("Suspicious PowerShell script detected: C:\\Temp\\exfil.ps1")
            
            if "Deleted File Recovery" in selected_analysis:
                st.markdown("#### Deleted File Recovery Results")
                
                deleted_files = [
                    {"Path": "C:\\Temp\\passwords.txt", "Size": "1.2 KB", "Deleted": "2023-04-15 08:42:30", "Recovery Status": "Complete"},
                    {"Path": "C:\\Temp\\connections.log", "Size": "5.6 KB", "Deleted": "2023-04-15 08:42:35", "Recovery Status": "Complete"},
                    {"Path": "C:\\Temp\\target-list.csv", "Size": "8.9 KB", "Deleted": "2023-04-15 08:42:40", "Recovery Status": "Partial"},
                ]
                
                deleted_df = pd.DataFrame(deleted_files)
                st.dataframe(deleted_df, use_container_width=True)
                
                st.success("3 deleted files recovered")

# REAL-TIME RESPONSE TAB
with tabs[4]:
    st.markdown("### Real-Time Response Tools")
    st.caption("Tools for live response to security incidents")
    
    response_tools = ["Network Scanning", "Process Analysis", "Endpoint Quarantine", "Traffic Capture"]
    selected_response_tool = st.selectbox("Select Response Tool", options=response_tools)
    
    if selected_response_tool == "Network Scanning":
        st.markdown("#### Network Scanning")
        
        scan_target = st.text_input("Target IP/Range", placeholder="192.168.1.0/24")
        
        scan_type = st.radio(
            "Scan Type",
            options=["Host Discovery", "Port Scanning", "OS Detection", "Vulnerability Scan"]
        )
        
        scan_options = st.expander("Scan Options")
        with scan_options:
            if scan_type == "Host Discovery":
                st.checkbox("ICMP Echo", value=True)
                st.checkbox("TCP SYN to port 443", value=True)
                st.checkbox("TCP ACK to port 80", value=False)
                st.checkbox("UDP scan", value=False)
            elif scan_type == "Port Scanning":
                st.slider("Port Range Start", 1, 1000, 1)
                st.slider("Port Range End", 1, 65535, 1000)
                st.checkbox("TCP Connect", value=True)
                st.checkbox("TCP SYN", value=False)
                st.checkbox("UDP Scan", value=False)
            elif scan_type == "OS Detection":
                st.checkbox("TCP/IP Stack Fingerprinting", value=True)
                st.checkbox("ICMP Echo", value=True)
                st.checkbox("TCP SYN to common ports", value=True)
        
        if st.button("Run Scan (Demo)"):
            st.info("Network scan would be performed here (demonstration)")
            
            if scan_type == "Host Discovery":
                st.markdown("#### Host Discovery Results")
                
                hosts = []
                for i in range(1, 6):
                    hosts.append({
                        "IP Address": f"192.168.1.{random.randint(1, 254)}",
                        "Status": "Up",
                        "Hostname": f"host-{random.randint(1, 100)}",
                        "MAC Address": f"00:1A:2B:{random.randint(10, 99)}:{random.randint(10, 99)}:{random.randint(10, 99)}",
                        "MAC Vendor": random.choice(["Cisco", "Dell", "HP", "Intel"])
                    })
                
                hosts_df = pd.DataFrame(hosts)
                st.dataframe(hosts_df, use_container_width=True)
                
                st.success(f"Found {len(hosts)} active hosts")
            
            elif scan_type == "Port Scanning":
                st.markdown("#### Port Scan Results")
                
                ports = []
                for host in ["192.168.1.100", "192.168.1.101"]:
                    for port, service in [
                        (21, "FTP"), 
                        (22, "SSH"), 
                        (80, "HTTP"), 
                        (443, "HTTPS"), 
                        (3389, "RDP")
                    ]:
                        if random.random() > 0.3:  # 70% chance of port being open
                            ports.append({
                                "Host": host,
                                "Port": port,
                                "Protocol": "tcp",
                                "State": "open",
                                "Service": service,
                                "Version": f"{service} {random.randint(1, 9)}.{random.randint(0, 9)}"
                            })
                
                ports_df = pd.DataFrame(ports)
                st.dataframe(ports_df, use_container_width=True)
                
                st.success(f"Scan complete: found {len(ports)} open ports")
    
    elif selected_response_tool == "Process Analysis":
        st.markdown("#### Remote Process Analysis")
        
        target_host = st.text_input("Target Host", placeholder="hostname or IP")
        
        if st.button("Get Running Processes (Demo)"):
            st.info(f"Retrieving processes from {target_host} (demonstration)")
            
            processes = [
                {"PID": 4, "Name": "System", "Memory": "88 KB", "CPU": "0.1%", "User": "SYSTEM", "Command Line": "N/A"},
                {"PID": 504, "Name": "lsass.exe", "Memory": "16 MB", "CPU": "0.2%", "User": "SYSTEM", "Command Line": "C:\\Windows\\System32\\lsass.exe"},
                {"PID": 324, "Name": "svchost.exe", "Memory": "24 MB", "CPU": "0.5%", "User": "SYSTEM", "Command Line": "C:\\Windows\\System32\\svchost.exe -k LocalService"},
                {"PID": 1876, "Name": "explorer.exe", "Memory": "48 MB", "CPU": "1.2%", "User": "user1", "Command Line": "C:\\Windows\\explorer.exe"},
                {"PID": 2456, "Name": "chrome.exe", "Memory": "286 MB", "CPU": "5.6%", "User": "user1", "Command Line": "C:\\Program Files\\Google\\Chrome\\chrome.exe --type=renderer"},
                {"PID": 3012, "Name": "suspicious.exe", "Memory": "2 MB", "CPU": "3.2%", "User": "user1", "Command Line": "C:\\Temp\\suspicious.exe -h 192.168.1.100 -p 8080"}
            ]
            
            processes_df = pd.DataFrame(processes)
            st.dataframe(processes_df, use_container_width=True)
            
            # Highlight suspicious process
            st.warning("Suspicious process detected: PID 3012 (suspicious.exe)")
            
            # Actions for selected process
            selected_pid = st.selectbox("Select process for action", options=[p["PID"] for p in processes])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Kill Process"):
                    st.success(f"Process {selected_pid} terminated (demo)")
            with col2:
                if st.button("Dump Memory"):
                    st.success(f"Memory dump created for process {selected_pid} (demo)")
            with col3:
                if st.button("Analyze"):
                    st.info(f"Detailed analysis of process {selected_pid} (demo)")
                    
                    # Show some fake process details
                    st.markdown("#### Process Details")
                    
                    process = next((p for p in processes if p["PID"] == selected_pid), None)
                    if process:
                        st.markdown(f"**Process Name:** {process['Name']}")
                        st.markdown(f"**PID:** {process['PID']}")
                        st.markdown(f"**User:** {process['User']}")
                        st.markdown(f"**Command Line:** {process['Command Line']}")
                        
                        if process["Name"] == "suspicious.exe":
                            st.error("This process exhibits suspicious behavior:")
                            st.markdown("- Connecting to external IP (192.168.1.100:8080)")
                            st.markdown("- Not digitally signed")
                            st.markdown("- Recently created executable")
                            st.markdown("- Running from temporary directory")
    
    elif selected_response_tool == "Endpoint Quarantine":
        st.markdown("#### Endpoint Quarantine")
        
        target_endpoint = st.text_input("Target Host", placeholder="hostname or IP")
        
        quarantine_options = st.multiselect(
            "Quarantine Options",
            options=["Block Network Access", "Disable User Account", "Kill Suspicious Processes", "Collect Evidence"],
            default=["Block Network Access"]
        )
        
        if st.button("Quarantine Endpoint (Demo)"):
            st.warning(f"Quarantining {target_endpoint} with selected options (demonstration)")
            
            for option in quarantine_options:
                st.success(f"Applied: {option}")
            
            st.info("Endpoint quarantined successfully (demo)")
            
            # Sample quarantine log
            st.markdown("#### Quarantine Log")
            
            log_entries = [
                {"Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Action": "Quarantine initiated", "Status": "Success", "Details": "Quarantine command issued"},
                {"Timestamp": (datetime.datetime.now() + datetime.timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S"), "Action": "Network isolation", "Status": "Success", "Details": "All non-management traffic blocked"}
            ]
            
            for i, option in enumerate(quarantine_options):
                if option != "Block Network Access":  # Already included above
                    log_entries.append({
                        "Timestamp": (datetime.datetime.now() + datetime.timedelta(seconds=3+i)).strftime("%Y-%m-%d %H:%M:%S"),
                        "Action": option,
                        "Status": "Success",
                        "Details": f"Successfully applied {option}"
                    })
            
            log_df = pd.DataFrame(log_entries)
            st.dataframe(log_df, use_container_width=True)
    
    elif selected_response_tool == "Traffic Capture":
        st.markdown("#### Network Traffic Capture")
        
        capture_interface = st.selectbox(
            "Capture Interface",
            options=["eth0", "eth1", "all interfaces"]
        )
        
        capture_filter = st.text_input(
            "Capture Filter",
            placeholder="host 192.168.1.100 and port 80",
            help="Enter a filter using pcap filter syntax"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            capture_duration = st.number_input(
                "Capture Duration (seconds)",
                min_value=10,
                max_value=3600,
                value=60
            )
        
        with col2:
            max_packet_count = st.number_input(
                "Maximum Packets",
                min_value=100,
                max_value=100000,
                value=1000
            )
        
        if st.button("Start Capture (Demo)"):
            st.info(f"Starting packet capture on {capture_interface} (demonstration)")
            
            # Simulate a packet capture progress bar
            progress_bar = st.progress(0)
            
            # Mock packet data for display
            packet_data = []
            for i in range(10):
                progress_bar.progress((i+1) * 10)
                
                protocol = random.choice(["TCP", "UDP", "HTTP", "DNS", "ICMP"])
                src_ip = f"192.168.1.{random.randint(1, 254)}"
                dst_ip = f"192.168.2.{random.randint(1, 254)}"
                
                # Generate packet details based on protocol
                if protocol == "TCP":
                    src_port = random.randint(49152, 65535)
                    dst_port = random.choice([80, 443, 22, 3389])
                    flags = random.choice(["SYN", "SYN+ACK", "ACK", "FIN", "RST"])
                    info = f"TCP {src_port} → {dst_port} [{flags}] Seq=1 Win=64240 Len=0"
                elif protocol == "UDP":
                    src_port = random.randint(49152, 65535)
                    dst_port = random.choice([53, 161, 123, 5353])
                    info = f"UDP {src_port} → {dst_port} Len={random.randint(50, 500)}"
                elif protocol == "HTTP":
                    method = random.choice(["GET", "POST", "PUT", "DELETE"])
                    resource = random.choice(["/index.html", "/api/v1/users", "/login", "/images/logo.png"])
                    info = f"{method} {resource} HTTP/1.1"
                elif protocol == "DNS":
                    query_type = random.choice(["A", "AAAA", "MX", "CNAME", "TXT"])
                    domain = random.choice(["example.com", "google.com", "microsoft.com", "aws.amazon.com"])
                    info = f"DNS Query {query_type} {domain}"
                else:  # ICMP
                    icmp_type = random.choice([0, 8])
                    type_name = "Echo reply" if icmp_type == 0 else "Echo request"
                    info = f"ICMP {type_name} id={random.randint(1, 65535)}, seq={random.randint(1, 100)}"
                
                packet = {
                    "No.": i+1,
                    "Time": f"{i * 0.12:.6f}",
                    "Source": src_ip,
                    "Destination": dst_ip,
                    "Protocol": protocol,
                    "Length": random.randint(64, 1500),
                    "Info": info
                }
                packet_data.append(packet)
                
                time.sleep(0.1)  # Simulate processing time
            
            # Display packet capture results
            st.success(f"Captured {len(packet_data)} packets")
            
            # Display captured packets
            packets_df = pd.DataFrame(packet_data)
            st.dataframe(packets_df, use_container_width=True)
            
            # Option to save capture
            st.download_button(
                label="Save Capture (Demo)",
                data=base64.b64encode(b"Mock PCAP data").decode(),
                file_name="capture.pcap",
                mime="application/octet-stream"
            )

# Footer
st.divider()
st.caption("© 2025 - nSocCSP | Incident Response Module | Last updated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))