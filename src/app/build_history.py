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

def get_build_url(commit_id):
    """Generate a unique URL for a specific build."""
    return f"https://github.com/DD2480Group8/DD2480-CI/commit/{commit_id}"

def clone_check_DB(repo_url, branch):
    """Clone the repository and perform syntax checking."""
    import tempfile
    import shutil
    from git import Repo
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"Cloning {repo_url} branch {branch} to {temp_dir}")  
        repo = Repo.clone_from(repo_url, temp_dir, branch=branch)
        commit_id = repo.head.commit.hexsha  
        return commit_id, temp_dir
    except Exception as e:
        print(f"Error during clone: {e}")
        return None, None
    finally:
        shutil.rmtree(temp_dir)

def log_build(commit_id):
    """Log the build details to the database."""
    try:
        print(f"Logging build for commit: {commit_id}")
        conn = sqlite3.connect('build_history.db')
        cursor = conn.cursor()
        build_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        build_url = get_build_url(commit_id)  
        cursor.execute('''
            INSERT INTO builds (commit_id, build_date, build_url)
            VALUES (?, ?, ?)
        ''', (commit_id, build_date, build_url))
        conn.commit()
        conn.close()
        print(f"Build logged: {commit_id} on {build_date}, URL: {build_url}")
    except Exception as e:
        print(f"Error logging build: {e}")