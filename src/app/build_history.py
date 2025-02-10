import sqlite3
from datetime import datetime
def create_database():
    """Create the database and the 'builds' table if it doesn't exist."""
    print("Creating database and table if not exists.")  
    try:
        print("Connecting to the database...")
        conn = sqlite3.connect('build_history.db')  
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS builds (
                id INTEGER PRIMARY KEY,
                commit_id TEXT,
                build_date TEXT,
                build_url TEXT  
            )
        ''')
        conn.commit()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables after creation: {tables}")  
        
        conn.close()
        print("Database created and table initialized successfully.")
    except Exception as e:
        print(f"Error during database creation: {e}")