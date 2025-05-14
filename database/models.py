from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum, create_engine, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
import os
import datetime

Base = declarative_base()

class DeviceStatus(enum.Enum):
    ONLINE = "online"
    WARNING = "warning"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class AlertSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NetworkDevice(Base):
    __tablename__ = 'network_devices'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(50), unique=True, nullable=False)
    device_name = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)
    manufacturer = Column(String(100))
    model = Column(String(100))
    ip_address = Column(String(50))
    mac_address = Column(String(50))
    os_version = Column(String(100))
    status = Column(Enum(DeviceStatus), default=DeviceStatus.OFFLINE)
    network = Column(String(100))
    location = Column(String(100))
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    performance_metrics = relationship("DevicePerformanceMetric", back_populates="device", cascade="all, delete-orphan")
    security_events = relationship("SecurityEvent", back_populates="device", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<NetworkDevice(id={self.id}, name='{self.device_name}', type='{self.device_type}')>"

class DevicePerformanceMetric(Base):
    __tablename__ = 'device_performance_metrics'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('network_devices.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_io = Column(Float)
    network_throughput = Column(Float)
    
    # Relationship
    device = relationship("NetworkDevice", back_populates="performance_metrics")
    
    def __repr__(self):
        return f"<DevicePerformanceMetric(id={self.id}, device_id={self.device_id}, timestamp='{self.timestamp}')>"

class SecurityEvent(Base):
    __tablename__ = 'security_events'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('network_devices.id'), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    event_type = Column(String(100), nullable=False)
    source_ip = Column(String(50))
    destination_ip = Column(String(50))
    description = Column(Text)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM)
    is_resolved = Column(Boolean, default=False)
    
    # Relationship
    device = relationship("NetworkDevice", back_populates="security_events")
    
    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, event_type='{self.event_type}', severity='{self.severity}')>"

class NetworkTraffic(Base):
    __tablename__ = 'network_traffic'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    source_ip = Column(String(50))
    destination_ip = Column(String(50))
    protocol = Column(String(20))
    port = Column(Integer)
    bytes_transferred = Column(Integer)
    packet_count = Column(Integer)
    
    def __repr__(self):
        return f"<NetworkTraffic(id={self.id}, source='{self.source_ip}', dest='{self.destination_ip}')>"

class TopologyChange(Base):
    __tablename__ = 'topology_changes'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    change_type = Column(String(50), nullable=False)
    device_id = Column(String(50))
    device_type = Column(String(50))
    details = Column(Text)
    
    def __repr__(self):
        return f"<TopologyChange(id={self.id}, change_type='{self.change_type}', device_id='{self.device_id}')>"

class NetworkConfiguration(Base):
    __tablename__ = 'network_configurations'
    
    id = Column(Integer, primary_key=True)
    network_address = Column(String(50), nullable=False)
    network_name = Column(String(100), nullable=False)
    monitor = Column(Boolean, default=True)
    scan_schedule = Column(String(20), default='hourly')
    alert_email = Column(String(100))
    alert_threshold = Column(String(20), default='medium')
    enabled_tools = Column(JSON)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<NetworkConfiguration(name='{self.network_name}', address='{self.network_address}')>"