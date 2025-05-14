from database.models import Base
from sqlalchemy import create_engine
import os

# Get database URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

def create_tables():
    print(f"Creating database tables using URL: {DATABASE_URL}")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()