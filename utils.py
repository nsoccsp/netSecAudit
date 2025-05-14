import streamlit as st
import datetime
import time
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from math import sin, cos, radians
import urllib.request
import json

# Cache the image loading to avoid repeated API calls
@st.cache_data
def load_image(query, index=0):
    """
    Load an image from the provided stock images.
    Args:
        query: The query string used to find the image
        index: The index of the image to use
        
    Returns:
        URL to the image if found, None otherwise
    """
    image_mappings = {
        "network security monitoring": [
            "https://pixabay.com/get/g861519ec27994fa594c974795bc00c023935c5b40e5bfc50a69a7020b9d0f653e03289d53c4e246f514b70a461f54c69a893b6e45b53de5fd6c7e9c293b7f6f9_1280.jpg",
            "https://pixabay.com/get/gdc3a38e3e42ebbb448dae93ddf1f05b63207dedc48d5ed550ccd516910efd587354be4357d8493b117497d6181c803717a0296dbd96841e37c3c3c85fb43efba_1280.jpg",
            "https://pixabay.com/get/gd342e4a5ac6a455f06ab4972d3da181c634e693e5f3c972e77bd7ef7b248ff769914a9863a6655f2a5658e68b73a510af90745430eca16b00e052805e7bc7e80_1280.jpg",
            "https://pixabay.com/get/g3cd079ceb002f73c25904bc92b194bb2cb0c6aa56c6fbfe2bb89d74fc2ff33cc5e20228213fbdef1da92e3a91b1a28f678cad84e9023c4a62e35ad2606b0e5ed_1280.jpg"
        ],
        "cybersecurity dashboard": [
            "https://pixabay.com/get/g209ee898a80ddd319d9ccd3ea90ff8ba28543689253df30a104d4137d0aa724efe8373ffa445c9d8aaf67b6133e7f38f3b4b6c9c6716e0393740310188a1bc24_1280.jpg",
            "https://pixabay.com/get/ge61a6c24764c476a10be7374c8dd700be45b781dcfeafca30e2837158edb5d1eb42dee41c739a321a082a1785a257bbb1f1d674c9476866ca9d943f653edfad7_1280.jpg",
            "https://pixabay.com/get/gffcf432348ae425f722cd706631e208603e086e513a500e6a091f2c56432b919f61400ab06cc304b682974b5c42c0357f3c176e2a9fe97e9ee986d9214d8ea7f_1280.jpg",
            "https://pixabay.com/get/g95936f73f40fca3a3881844227ba724e12a5c56676df58121ff3526146cd1a5e91638b5d4117c340223a4442a013f313f2b54c9950371d8baebdbd2943a1d67e_1280.jpg"
        ],
        "network traffic visualization": [
            "https://pixabay.com/get/g2a66addeba13910dc5f0306eedfcc9186f111ac20afee15dbdd635065f6fc06163166dd3232a6185e85fa134f66031f93aa4e5a1dd27f54c9dabd119d4d53973_1280.jpg",
            "https://pixabay.com/get/gbc822417b24f8c3371a367dce165b7072391dc04073e7dadd2800f1810948387bc649bb0e93de667f9d3006417d80ca71f2219d08e10f00f80c94fcc066568d8_1280.jpg"
        ]
    }
    
    if query in image_mappings and index < len(image_mappings[query]):
        return image_mappings[query][index]
    return None

def get_current_phase():
    """
    Calculate the current phase based on the current date.
    For demonstration purposes, we'll assume a start date 
    and calculate the current phase based on that.
    
    Returns:
        Tuple: (phase_number, phase_description)
    """
    # For demonstration, we'll calculate phases relative to app run time
    # In a real application, this would be based on actual project timeline
    current_time = time.time()
    # Use a "fixed" start time (app launch time in session state)
    if 'project_start_time' not in st.session_state:
        st.session_state.project_start_time = current_time
        
    # Compress the timeline for demo purposes (1 day = 1 week)
    elapsed_weeks = int((current_time - st.session_state.project_start_time) / (60 * 60 * 24))
    
    if elapsed_weeks < 2:
        return 1, "Inventory, topology, and documentation"
    elif elapsed_weeks < 6:
        return 2, "SNMP/sFlow, alerting, STP tracking"
    elif elapsed_weeks < 10:
        return 3, "VLAN correctness, rogue devices, loop control"
    else:
        return 4, "Regular audits, updates, and optimizations"

def get_phase_progress():
    """
    Calculate the progress within the current phase.
    
    Returns:
        float: Progress percentage (0.0 to 1.0)
    """
    current_time = time.time()
    
    if 'project_start_time' not in st.session_state:
        st.session_state.project_start_time = current_time
        
    elapsed_days = (current_time - st.session_state.project_start_time) / (60 * 60 * 24)
    current_phase, _ = get_current_phase()
    
    if current_phase == 1:
        # Phase 1: Weeks 1-2 (days 0-14)
        return min(elapsed_days / 14, 1.0)
    elif current_phase == 2:
        # Phase 2: Weeks 3-6 (days 14-42)
        return min((elapsed_days - 14) / 28, 1.0)
    elif current_phase == 3:
        # Phase 3: Weeks 7-10 (days 42-70)
        return min((elapsed_days - 42) / 28, 1.0)
    else:
        # Ongoing phase
        return 0.0  # Continuous progress

def create_network_graph(num_nodes=20, num_edges=30):
    """
    Create a random network graph for visualization.
    
    Args:
        num_nodes: Number of nodes in the graph
        num_edges: Number of edges to create
        
    Returns:
        tuple: (G, pos, edge_x, edge_y, node_x, node_y, node_text, node_size)
    """
    # Create a graph
    G = nx.Graph()
    
    # Add nodes
    for i in range(num_nodes):
        node_type = random.choice(['server', 'router', 'switch', 'client'])
        node_status = random.choice(['online', 'online', 'online', 'warning', 'offline'])
        G.add_node(i, type=node_type, status=node_status)
    
    # Add edges (connections)
    while len(G.edges) < num_edges:
        u = random.randint(0, num_nodes-1)
        v = random.randint(0, num_nodes-1)
        if u != v:
            G.add_edge(u, v)
    
    # Create positions for nodes in a circle layout
    pos = {}
    radius = 5
    for i in range(num_nodes):
        angle = i * (360 / num_nodes)
        pos[i] = (radius * cos(radians(angle)), radius * sin(radians(angle)))
    
    # Create edge traces
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        node_type = G.nodes[node]['type']
        node_status = G.nodes[node]['status']
        
        # Set node size based on type
        if node_type == 'server':
            size = 15
        elif node_type in ['router', 'switch']:
            size = 12
        else:
            size = 8
        node_size.append(size)
        
        # Set node color based on status
        if node_status == 'online':
            color = 'green'
        elif node_status == 'warning':
            color = 'orange'
        else:  # offline
            color = 'red'
        node_color.append(color)
        
        # Create node hover text
        node_text.append(f"ID: {node}<br>Type: {node_type}<br>Status: {node_status}")
    
    return G, pos, edge_x, edge_y, node_x, node_y, node_text, node_size, node_color

def format_size(size_bytes):
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"

def get_random_ip():
    """Generate a random IP address"""
    return f"{random.randint(10, 192)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def get_random_mac():
    """Generate a random MAC address"""
    return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
