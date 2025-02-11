import sqlite3
from datetime import datetime

def create_database(table_name='builds'):
    """Create the database and the specified table if it doesn't exist."""
    print(f"Creating database and table '{table_name}' if not exists.")  
    try:
        print("Connecting to the database...")
        conn = sqlite3.connect('build_history.db')  
        cursor = conn.cursor()
        
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY,
                commit_id TEXT,
                build_date TEXT,
                build_logs TEXT,
                build_url TEXT  
            )
        ''')
        conn.commit()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables after creation: {tables}")  
        
        conn.close()
        print(f"Database created and table '{table_name}' initialized successfully.")
    except Exception as e:
        print(f"Error during database creation: {e}")

def get_build_url(commit_id):
    """Generate a unique URL for a specific build."""
    return f"https://github.com/DD2480Group8/DD2480-CI/commit/{commit_id}"

def log_build(commit_id, build_logs=None, table_name='builds'):
    """Log the build details to the specified table in the database."""
    try:
        print(f"Logging build for commit: {commit_id} in table '{table_name}'")
        conn = sqlite3.connect('build_history.db')
        cursor = conn.cursor()
        build_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        build_url = get_build_url(commit_id)  
        cursor.execute(f'''
            INSERT INTO {table_name} (commit_id, build_date, build_logs, build_url)
            VALUES (?, ?, ?, ?)
        ''', (commit_id, build_date, build_logs if build_logs else 'No logs available', build_url))
        conn.commit()
        conn.close()
        print(f"Build logged: {commit_id} on {build_date}, \nLogs: {build_logs} \nURL: {build_url}")
    except Exception as e:
        print(f"Error logging build: {e}")

