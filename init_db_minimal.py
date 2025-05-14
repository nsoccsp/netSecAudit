import os
import datetime
import random
from sqlalchemy import create_engine
from database.models import Base, NetworkDevice, DeviceStatus

# Get database URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

def initialize_minimal_database():
    """Initialize just the database tables without adding any data"""
    print("Initializing database tables...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("Database tables created successfully!")

if __name__ == "__main__":
    initialize_minimal_database()