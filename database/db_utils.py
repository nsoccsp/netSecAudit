from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
import datetime
from .models import Base, NetworkDevice, DevicePerformanceMetric, SecurityEvent, NetworkTraffic, TopologyChange, DeviceStatus, AlertSeverity, NetworkConfiguration

# Get database URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    db_url = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'nsoccsp')}"
    try:
        engine = create_engine(db_url)
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise
else:
    try:
        engine = create_engine(DATABASE_URL)
    except Exception as e:
        print(f"Error connecting to the database using DATABASE_URL: {e}")
        raise

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def init_db():
    """Initialize the database by creating all tables"""
    try:
        Base.metadata.create_all(engine)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def get_session():
    """Get a database session."""
    session = Session()
    try:
        return session
    except Exception as e:
        session.rollback()
        print(f"Error getting database session: {e}")
        raise
    finally:
        session.close()

def add_network_device(device_data):
    """Add a new network device to the database"""
    session = get_session()
    try:
        # Convert string status to enum value
        if isinstance(device_data.get('status'), str):
            device_data['status'] = DeviceStatus(device_data['status'])

        device = NetworkDevice(**device_data)
        session.add(device)
        session.commit()
        return device.id
    except Exception as e:
        session.rollback()
        print(f"Error adding network device: {e}")
        raise
    finally:
        session.close()

def get_network_devices(filters=None):
    """Get all network devices, optionally filtered"""
    session = get_session()
    try:
        query = session.query(NetworkDevice)

        if filters:
            if 'device_type' in filters and filters['device_type']:
                query = query.filter(NetworkDevice.device_type.in_(filters['device_type']))
            if 'status' in filters and filters['status']:
                status_enums = [DeviceStatus(s) for s in filters['status']]
                query = query.filter(NetworkDevice.status.in_(status_enums))
            if 'network' in filters and filters['network']:
                query = query.filter(NetworkDevice.network.in_(filters['network']))

        devices = query.all()
        return [device_to_dict(device) for device in devices]
    finally:
        session.close()

def device_to_dict(device):
    """Convert a NetworkDevice object to a dictionary"""
    result = {c.name: getattr(device, c.name) for c in device.__table__.columns}
    # Convert enum to string
    if isinstance(result['status'], DeviceStatus):
        result['status'] = result['status'].value
    # Convert datetime to string
    if isinstance(result['last_updated'], datetime.datetime):
        result['last_updated'] = result['last_updated'].strftime('%Y-%m-%d %H:%M:%S')
    return result

def add_security_event(event_data):
    """Add a new security event to the database"""
    session = get_session()
    try:
        # Convert string severity to enum value
        if isinstance(event_data.get('severity'), str):
            event_data['severity'] = AlertSeverity(event_data['severity'])

        event = SecurityEvent(**event_data)
        session.add(event)
        session.commit()
        return event.id
    except Exception as e:
        session.rollback()
        print(f"Error adding security event: {e}")
        raise
    finally:
        session.close()

def get_security_events(filters=None):
    """Get all security events, optionally filtered"""
    session = get_session()
    try:
        query = session.query(SecurityEvent)

        if filters:
            if 'event_type' in filters and filters['event_type']:
                query = query.filter(SecurityEvent.event_type.in_(filters['event_type']))
            if 'severity' in filters and filters['severity']:
                severity_enums = [AlertSeverity(s) for s in filters['severity']]
                query = query.filter(SecurityEvent.severity.in_(severity_enums))
            if 'is_resolved' in filters:
                query = query.filter(SecurityEvent.is_resolved == filters['is_resolved'])

        events = query.order_by(SecurityEvent.timestamp.desc()).all()
        return [event_to_dict(event) for event in events]
    finally:
        session.close()

def event_to_dict(event):
    """Convert a SecurityEvent object to a dictionary"""
    result = {c.name: getattr(event, c.name) for c in event.__table__.columns}
    # Convert enum to string
    if isinstance(result['severity'], AlertSeverity):
        result['severity'] = result['severity'].value
    # Convert datetime to string
    if isinstance(result['timestamp'], datetime.datetime):
        result['timestamp'] = result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    return result

def add_device_performance_metric(metric_data):
    """Add a new device performance metric to the database"""
    session = get_session()
    try:
        metric = DevicePerformanceMetric(**metric_data)
        session.add(metric)
        session.commit()
        return metric.id
    except Exception as e:
        session.rollback()
        print(f"Error adding device performance metric: {e}")
        raise
    finally:
        session.close()

def get_device_performance_metrics(device_id=None, hours=24):
    """Get device performance metrics for a specific device and time range"""
    session = get_session()
    try:
        query = session.query(DevicePerformanceMetric)

        if device_id:
            query = query.filter(DevicePerformanceMetric.device_id == device_id)

        # Filter by time range
        time_cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
        query = query.filter(DevicePerformanceMetric.timestamp >= time_cutoff)

        metrics = query.order_by(DevicePerformanceMetric.timestamp).all()
        return [metric_to_dict(metric) for metric in metrics]
    finally:
        session.close()

def metric_to_dict(metric):
    """Convert a DevicePerformanceMetric object to a dictionary"""
    result = {c.name: getattr(metric, c.name) for c in metric.__table__.columns}
    # Convert datetime to string
    if isinstance(result['timestamp'], datetime.datetime):
        result['timestamp'] = result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    return result

def add_network_traffic(traffic_data):
    """Add a new network traffic record to the database"""
    session = get_session()
    try:
        traffic = NetworkTraffic(**traffic_data)
        session.add(traffic)
        session.commit()
        return traffic.id
    except Exception as e:
        session.rollback()
        print(f"Error adding network traffic record: {e}")
        raise
    finally:
        session.close()

def get_network_traffic(hours=24):
    """Get network traffic data for a specific time range"""
    session = get_session()
    try:
        # Filter by time range
        time_cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
        query = session.query(NetworkTraffic).filter(NetworkTraffic.timestamp >= time_cutoff)

        traffic = query.order_by(NetworkTraffic.timestamp).all()
        return [traffic_to_dict(record) for record in traffic]
    finally:
        session.close()

def traffic_to_dict(traffic):
    """Convert a NetworkTraffic object to a dictionary"""
    result = {c.name: getattr(traffic, c.name) for c in traffic.__table__.columns}
    # Convert datetime to string
    if isinstance(result['timestamp'], datetime.datetime):
        result['timestamp'] = result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    return result

def add_topology_change(change_data):
    """Add a new topology change record to the database"""
    session = get_session()
    try:
        change = TopologyChange(**change_data)
        session.add(change)
        session.commit()
        return change.id
    except Exception as e:
        session.rollback()
        print(f"Error adding topology change record: {e}")
        raise
    finally:
        session.close()

def get_topology_changes(num_changes=20):
    """Get the most recent topology changes"""
    session = get_session()
    try:
        changes = session.query(TopologyChange).order_by(TopologyChange.timestamp.desc()).limit(num_changes).all()
        return [change_to_dict(change) for change in changes]
    finally:
        session.close()

def change_to_dict(change):
    """Convert a TopologyChange object to a dictionary"""
    result = {c.name: getattr(change, c.name) for c in change.__table__.columns}
    # Convert datetime to string
    if isinstance(result['timestamp'], datetime.datetime):
        result['timestamp'] = result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    return result

def save_network_configuration(config_data):
    """Save network configuration to database"""
    session = get_session()
    try:
        # Delete existing configurations
        session.query(NetworkConfiguration).delete()
        
        # Add new configurations
        for network in config_data["networks"]:
            config = NetworkConfiguration(
                network_address=network["address"],
                network_name=network["name"],
                monitor=network["monitor"],
                scan_schedule=config_data["scan_schedule"],
                alert_email=config_data["alert_email"],
                alert_threshold=config_data["alert_threshold"],
                enabled_tools=config_data["enabled_tools"]
            )
            session.add(config)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error saving network configuration: {e}")
        raise
    finally:
        session.close()

def get_network_configurations():
    """Get all network configurations"""
    session = get_session()
    try:
        configs = session.query(NetworkConfiguration).all()
        return configs
    except Exception as e:
        print(f"Error retrieving network configurations: {e}")
        raise
    finally:
        session.close()