import sqlite3
from datetime import datetime

def create_database(table_name='builds'):
    """Create the database and the specified table if it doesn't exist, and add missing columns."""
    print(f"Creating database and table '{table_name}' if not exists.")  
    try:
        print("Connecting to the database...")
        conn = sqlite3.connect('build_history.db')  
        cursor = conn.cursor()
        
        # Create the table if it doesn't exist
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY,
                commit_id TEXT,
                build_date TEXT,
                build_logs TEXT,
                github_commit_url TEXT  
            )
        ''')
        
        # Check if the 'build_logs' column exists, and add it if not
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if 'build_logs' not in column_names:
            print(f"Adding 'build_logs' column to table '{table_name}'.")
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN build_logs TEXT;")
        
        conn.commit()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables after creation: {tables}")  
        
        conn.close()
        print(f"Database created and table '{table_name}' initialized successfully.")
    except Exception as e:
        print(f"Error during database creation: {e}")

def get_github_commit_url(commit_id):
    """Generate a unique URL for a specific build."""
    return f"https://github.com/DD2480Group8/DD2480-CI/commit/{commit_id}"

def log_build(commit_id, build_logs=None, table_name='builds'):
    """Log the build details to the specified table in the database."""
    try:
        print(f"Logging build for commit: {commit_id} in table '{table_name}'")
        conn = sqlite3.connect('build_history.db')
        cursor = conn.cursor()
        build_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        github_commit_url = get_github_commit_url(commit_id)  
        cursor.execute(f'''
            INSERT INTO {table_name} (commit_id, build_date, build_logs, github_commit_url)
            VALUES (?, ?, ?, ?)
        ''', (commit_id, build_date, build_logs if build_logs else 'No logs available', github_commit_url))
        conn.commit()
        conn.close()
        print(f"Build logged: {commit_id} on {build_date}, \nLogs: {build_logs} \nURL: {github_commit_url}")
    except Exception as e:
        print(f"Error logging build: {e}")

def get_logs():
    """Retrieve all build logs from the database."""
    try:
        print("Retrieving build logs from database.")
        conn = sqlite3.connect('build_history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM builds")
        logs = cursor.fetchall()
        conn.close()
        print(f"Logs retrieved: {logs}")
        return logs
    except Exception as e:
        print(f"Error retrieving logs: {e}")
        return []

def get_log(id):
    """Retrieve a specific build log from the database."""
    try:
        print(f"Retrieving build log with id: {id}")
        conn = sqlite3.connect('build_history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM builds WHERE id=?", (id,))
        log = cursor.fetchone()
        conn.close()
        print(f"Log retrieved: {log}")
        return log
    except Exception as e:
        print(f"Error retrieving log: {e}")
        return None