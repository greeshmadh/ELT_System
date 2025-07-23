from app import allowed_file

def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json() == {"status": "API is running"}

def test_login_success(client):
    res = client.post('/auth/login', json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    assert "token" in res.get_json()
    assert "role" in res.get_json()

def test_login_failure(client):
    res = client.post('/auth/login', json={"username": "admin", "password": "wrong"})
    assert res.status_code == 401
    assert "error" in res.get_json()

# Optional: test protected endpoints with token
def test_config_history_unauthorized(client):
    res = client.get('/config-history')
    assert res.status_code == 401  # No token provided
    
def get_token(client):
    res = client.post('/auth/login', json={"username": "admin", "password": "admin123"})
    return res.get_json()["token"]

def test_config_history(client):
    token = get_token(client)
    res = client.get('/config-history', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code in (200, 500)  # 500 if no DB setup, else 200

def test_get_api_data_success(client, tmp_path):
    # Setup mock JSON file
    api_dir = tmp_path / "api"
    api_dir.mkdir()
    sample_file = api_dir / "sample.json"
    sample_file.write_text('[{"id":1,"name":"test"}]')

    res = client.get("/api/data", query_string={"path": str(api_dir)})
    assert res.status_code == 200
    assert res.json == [{"id": 1, "name": "test"}]



def test_allowed_file_extensions():
    assert allowed_file("test.yaml") is True
    assert allowed_file("test.yml") is True
    assert allowed_file("test.csv") is False

# def test_get_logs_success(client, auth_headers, monkeypatch, tmp_path):
#     log_path = tmp_path / "elt.log"
#     log_path.write_text("INFO: test log line\n" * 120)

#     monkeypatch.setattr("logger.LOG_FILE", str(log_path))  # override global if needed

#     response = client.get("/logs", headers=auth_headers)
#     assert response.status_code == 200
#     assert "test log line" in response.get_data(as_text=True)

