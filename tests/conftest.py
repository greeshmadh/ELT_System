import pytest
import sys
import os
import pytest
  # your main Flask app

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def auth_headers():
    # Simulate a JWT token - ideally generate dynamically or mock
    token = "your_test_jwt_token"  # Replace with a real or mocked token if needed
    return {
        "Authorization": f"Bearer {token}"
    }



from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
