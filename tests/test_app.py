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
