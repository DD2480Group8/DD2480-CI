import pytest
import sqlite3
from app.build_history import create_database, get_build_url, log_build

@pytest.fixture(scope="module")
def setup_db():
    """Setup the test database and create a 'test_builds' table."""
    create_database('test_builds')  
    yield
    # Cleanup after tests
    conn = sqlite3.connect('build_history.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS test_builds")
    conn.commit()
    conn.close()

