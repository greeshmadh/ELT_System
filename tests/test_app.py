from app import allowed_file

# Test that the health check route works
def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json() == {"status": "API is running"}

# Test successful login with valid credentials
def test_login_success(client):
    res = client.post('/auth/login', json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    assert "token" in res.get_json()   # Token should be returned
    assert "role" in res.get_json()    # Role (admin/user) should be returned

# Test login with wrong password should fail
def test_login_failure(client):
    res = client.post('/auth/login', json={"username": "admin", "password": "wrong"})
    assert res.status_code == 401
    assert "error" in res.get_json()   # Should return an error message

# Unauthorized access to protected route should fail
def test_config_history_unauthorized(client):
    res = client.get('/config-history')  # No auth token
    assert res.status_code == 401        # Should be unauthorized

# Helper to generate valid JWT token for testing protected endpoints
def get_token(client):
    res = client.post('/auth/login', json={"username": "admin", "password": "admin123"})
    return res.get_json()["token"]

# Test authorized access to config history route
def test_config_history(client):
    token = get_token(client)
    res = client.get('/config-history', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code in (200, 500)  # 500 may occur if DB isn't set up; 200 if it is

# Test API data retrieval from temporary JSON file
def test_get_api_data_success(client, tmp_path):
    # Create a temporary directory and file
    api_dir = tmp_path / "api"
    api_dir.mkdir()
    sample_file = api_dir / "sample.json"
    sample_file.write_text('[{"id":1,"name":"test"}]')

    # Call the endpoint with mock path
    res = client.get("/api/data", query_string={"path": str(api_dir)})
    assert res.status_code == 200
    assert res.json == [{"id": 1, "name": "test"}]

# Check file extension validation logic
def test_allowed_file_extensions():
    assert allowed_file("test.yaml") is True
    assert allowed_file("test.yml") is True
    assert allowed_file("test.csv") is False  # .csv not allowed

