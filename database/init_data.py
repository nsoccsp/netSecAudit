import os
import datetime
import random
from database import (
    init_db,
    add_network_device,
    add_security_event,
    add_device_performance_metric,
    add_network_traffic,
    add_topology_change,
    DeviceStatus,
    AlertSeverity
)
from data.mock_generator import (
    generate_device_inventory,
    generate_security_events,
    generate_system_metrics,
    generate_network_traffic,
    generate_topology_changes,
    get_random_ip,
    get_random_mac
)

def initialize_database():
    """Initialize the database and seed it with initial data"""
    print("Initializing database...")
    
    # Create tables
    init_db()
    
    # Seed network devices
    print("Adding network devices...")
    devices = generate_device_inventory(50)
    device_ids = {}  # Map device_id to database id
    
    for device in devices:
        # Convert status string to enum value
        status_str = device['status']
        device['status'] = DeviceStatus(status_str)
            
        db_id = add_network_device(device)
        device_ids[device['device_id']] = db_id
    
    # Seed security events
    print("Adding security events...")
    events = generate_security_events(50)
    
    for event in events:
        # Link event to a random device
        if device_ids:
            random_device_id = random.choice(list(device_ids.values()))
            event['device_id'] = random_device_id
            
        # Convert severity string to enum value
        severity_str = event['severity']
        event['severity'] = AlertSeverity(severity_str)
        
        add_security_event(event)
    
    # Seed performance metrics
    print("Adding performance metrics...")
    for device_db_id in device_ids.values():
        # Add 24 hours of metrics for each device
        metrics = generate_system_metrics(24)
        
        for metric in metrics:
            metric_data = {
                'device_id': device_db_id,
                'timestamp': datetime.datetime.fromisoformat(metric['timestamp'].replace('Z', '+00:00')),
                'cpu_usage': metric['cpu_usage'],
                'memory_usage': metric['memory_usage'],
                'disk_io': metric['disk_io'],
                'network_throughput': metric['network_throughput']
            }
            add_device_performance_metric(metric_data)
    
    # Seed network traffic
    print("Adding network traffic data...")
    traffic_data = generate_network_traffic(24)
    
    for traffic in traffic_data:
        traffic_record = {
            'timestamp': datetime.datetime.fromisoformat(traffic['timestamp'].replace('Z', '+00:00')),
            'source_ip': traffic['source_ip'],
            'destination_ip': traffic['destination_ip'],
            'protocol': traffic['protocol'],
            'port': traffic['port'],
            'bytes_transferred': traffic['bytes_transferred'],
            'packet_count': random.randint(1, 100)
        }
        add_network_traffic(traffic_record)
    
    # Seed topology changes
    print("Adding topology changes...")
    topology_changes = generate_topology_changes(20)
    
    for change in topology_changes:
        change_record = {
            'timestamp': datetime.datetime.fromisoformat(change['timestamp'].replace('Z', '+00:00')),
            'change_type': change['change_type'],
            'device_id': change['device_id'],
            'device_type': change['device_type'],
            'details': change['details']
        }
        add_topology_change(change_record)
    
    print("Database initialization complete!")

if __name__ == "__main__":
    initialize_database()