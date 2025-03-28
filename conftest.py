import sys
import os
import pytest

# Add the project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Print debug information during test collection
print(f"Python version: {sys.version}")
print(f"Test directory: {project_root}")
print(f"sys.path: {sys.path}")

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up the test environment"""
    print("Setting up test environment")
    yield
    print("Tearing down test environment")