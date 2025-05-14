import sys
from database.init_data import initialize_database
from database.models import AlertSeverity

connection_string = "postgresql://postgres:postgres@localhost:5432/nsoccsp"

if __name__ == "__main__":
    try:
        initialize_database()
        print("Database initialized successfully")
    except Exception as e:

        print(f"Error initializing database: {e}")
        sys.exit(1)