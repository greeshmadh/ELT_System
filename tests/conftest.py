import pytest
import sys
import os
import pytest
from app import app

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def auth_headers():
    # Simulate a JWT token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MzM4MzgyOCwianRpIjoiOTQ4N2U3NjQtOTlkMS00YWU1LTgxYTctYmQyODkyNjlhMGE5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluIiwibmJmIjoxNzUzMzgzODI4LCJjc3JmIjoiZTgxMDliNDctOWRlZC00ZmQ5LTljM2UtNTNlODljY2UwNjZjIiwiZXhwIjoxNzUzMzg3NDI4fQ.QqGOFGSSITvmI_tZYcXNoA0GieS9GYoIoiiPfK7BGpE"  # Replace with a real or mocked token if needed
    return {
        "Authorization": f"Bearer {token}"
    }



@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
