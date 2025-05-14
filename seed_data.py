"""
Script to seed the database with initial sample data.
"""

import datetime
import random
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from data.mock_generator import (
    generate_device_inventory,
    generate_security_events,
    generate_network_traffic,
    generate_topology_changes,
    get_random_ip,
    generate_system_metrics
)
from database.models import (
    Base,
    NetworkDevice,
    DevicePerformanceMetric,
    SecurityEvent,
    NetworkTraffic,
    TopologyChange,
    DeviceStatus,
    AlertSeverity
)

# Get database URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def seed_devices(count=10):
    """Seed network devices"""
    print(f"Seeding {count} network devices...")
    
    devices = generate_device_inventory(count)
    device_ids = []
    
    for device_data in devices:
        # Convert status to enum
        status_str = device_data['status']
        
        # Create a device object
        device = NetworkDevice(
            device_id=device_data['device_id'],
            device_name=device_data['device_name'],
            device_type=device_data['device_type'],
            manufacturer=device_data['manufacturer'],
            model=device_data['model'],
            ip_address=device_data['ip_address'],
            mac_address=device_data['mac_address'],
            os_version=device_data['os_version'],
            status=DeviceStatus(status_str),
            network=device_data['network'],
            location=device_data['location'],
            last_updated=datetime.datetime.now()
        )
        
        session.add(device)
        session.flush()  # Flush to get the ID
        device_ids.append(device.id)
    
    session.commit()
    print(f"Added {len(device_ids)} devices")
    return device_ids

def seed_security_events(count=20, device_ids=None):
    """Seed security events"""
    print(f"Seeding {count} security events...")
    
    events = generate_security_events(count)
    
    for event_data in events:
        # Link to a random device if available
        device_id = None
        if device_ids:
            device_id = random.choice(device_ids)
            
        # Convert severity to enum and make it lowercase to match the enum values
        severity_str = event_data['severity']
        
        # Handle the timestamp (it's already a datetime object)
        timestamp = event_data['timestamp']
        
        # Create an event object
        event = SecurityEvent(
            device_id=device_id,
            timestamp=timestamp,
            event_type=event_data['event_type'],
            source_ip=event_data['source_ip'],
            destination_ip=event_data.get('destination_ip'),
            description=event_data['description'],
            severity=AlertSeverity(severity_str.lower()),
            is_resolved=event_data.get('is_resolved', False)
        )
        
        session.add(event)
    
    session.commit()
    print(f"Added {count} security events")

def seed_performance_metrics(device_ids, points_per_device=24):
    """Seed device performance metrics"""
    print(f"Seeding performance metrics for {len(device_ids)} devices...")
    
    for device_id in device_ids:
        metrics = generate_system_metrics(points_per_device)
        
        for metric_data in metrics:
            # Create a metric object
            metric = DevicePerformanceMetric(
                device_id=device_id,
                timestamp=metric_data['timestamp'],
                cpu_usage=metric_data['cpu_usage'],
                memory_usage=metric_data['memory_usage'],
                disk_io=metric_data['disk_io'],
                network_throughput=metric_data['network_throughput']
            )
            
            session.add(metric)
    
    session.commit()
    print(f"Added {len(device_ids) * points_per_device} performance metrics")

def seed_network_traffic(count=100):
    """Seed network traffic data"""
    print(f"Seeding {count} network traffic records...")
    
    traffic_data = generate_network_traffic(hours=24, count=count)
    
    for traffic in traffic_data:
        # Create a traffic object
        traffic_record = NetworkTraffic(
            timestamp=traffic['timestamp'],
            source_ip=traffic['source_ip'],
            destination_ip=traffic['destination_ip'],
            protocol=traffic['protocol'],
            port=traffic['port'],
            bytes_transferred=traffic['bytes_transferred'],
            packet_count=random.randint(1, 100)
        )
        
        session.add(traffic_record)
    
    session.commit()
    print(f"Added {count} network traffic records")

def seed_topology_changes(count=15):
    """Seed topology changes"""
    print(f"Seeding {count} topology changes...")
    
    changes = generate_topology_changes(count)
    
    for change_data in changes:
        # Create a topology change object
        change = TopologyChange(
            timestamp=change_data['timestamp'],
            change_type=change_data['change_type'],
            device_id=change_data['device_id'],
            device_type=change_data['device_type'],
            details=change_data['details']
        )
        
        session.add(change)
    
    session.commit()
    print(f"Added {count} topology changes")

def check_table_empty(table_name):
    """Check if a table is empty"""
    sql = text(f"SELECT COUNT(*) FROM {table_name}")
    result = session.execute(sql).scalar()
    return result == 0

def seed_database():
    """Seed the entire database with sample data"""
    try:
        print("Starting database seeding...")
        
        # Check if tables have data already
        devices_empty = check_table_empty('network_devices')
        events_empty = check_table_empty('security_events')
        metrics_empty = check_table_empty('device_performance_metrics')
        traffic_empty = check_table_empty('network_traffic')
        topology_empty = check_table_empty('topology_changes')
        
        device_ids = []
        
        # Seed devices only if empty
        if devices_empty:
            print("Seeding network devices...")
            device_ids = seed_devices(15)
        else:
            print("Network devices table already has data, skipping...")
            # Get existing device IDs
            sql = text("SELECT id FROM network_devices LIMIT 15")
            device_rows = session.execute(sql).fetchall()
            device_ids = [row[0] for row in device_rows]
        
        # Seed security events only if empty
        if events_empty:
            print("Seeding security events...")
            seed_security_events(30, device_ids)
        else:
            print("Security events table already has data, skipping...")
        
        # Seed performance metrics only if empty
        if metrics_empty:
            print("Seeding performance metrics...")
            seed_performance_metrics(device_ids)
        else:
            print("Performance metrics table already has data, skipping...")
        
        # Seed network traffic only if empty
        if traffic_empty:
            print("Seeding network traffic...")
            seed_network_traffic(120)
        else:
            print("Network traffic table already has data, skipping...")
        
        # Seed topology changes only if empty
        if topology_empty:
            print("Seeding topology changes...")
            seed_topology_changes(20)
        else:
            print("Topology changes table already has data, skipping...")
        
        print("Database seeding complete!")
    except Exception as e:
        session.rollback()
        print(f"Error during database seeding: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()