import pytest
import sqlite3
from app.build_history import create_database, get_github_commit_url, log_build

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

def test_get_github_commit_url():
    """Test if the build URL is generated correctly."""
    commit_id = "123abc"
    expected_url = "https://github.com/DD2480Group8/DD2480-CI/commit/123abc"
    assert get_github_commit_url(commit_id) == expected_url

def test_log_build(setup_db):
    """Test if a build is logged correctly into 'test_builds'."""
    commit_id = "123abc"
    build_logs = "Test passed"
    
    log_build(commit_id, build_logs, 'test_builds')
    conn = sqlite3.connect('build_history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_builds WHERE commit_id = ?", (commit_id,))
    result = cursor.fetchone()
    conn.close()

    assert result is not None, "The build should be logged in the database."
    assert result[1] == commit_id, f"Expected commit_id {commit_id}, got {result[1]}"
    assert result[2] == build_logs or "No logs available", f"Expected logs '{build_logs}', got '{result[2]}'"