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

def test_create_database(setup_db):
    """Test if the 'test_builds' table is created in the database."""
    conn = sqlite3.connect('build_history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()

    assert ('test_builds',) in tables, "The 'test_builds' table should exist in the database."

def test_get_build_url():
    """Test if the build URL is generated correctly."""
    commit_id = "123abc"
    expected_url = "https://github.com/DD2480Group8/DD2480-CI/commit/123abc"
    assert get_build_url(commit_id) == expected_url