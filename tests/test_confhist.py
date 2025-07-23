import io
import os
import tempfile
import pytest
import yaml
import shutil

from config_manager import app, upload_if_new_config

# ---------- FIXTURE: Flask client ----------
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    with app.test_client() as client:
        yield client
    shutil.rmtree(app.config['UPLOAD_FOLDER'])

# ---------- TEST: Upload valid YAML ----------
def test_upload_valid_yaml(client):
    yaml_content = b"source:\n  local:\n    path: 'mock.csv'"
    data = {
        'file': (io.BytesIO(yaml_content), 'test.yaml')
    }

    response = client.post('/upload-config', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert 'version' in response.get_json()
    assert 'message' in response.get_json()
    assert response.get_json()['message'] == 'YAML uploaded successfully'


# ---------- TEST: Upload with no file ----------
def test_upload_no_file(client):
    response = client.post('/upload-config')
    assert response.status_code == 400
    assert 'No file uploaded' in response.get_json()['error']


# ---------- TEST: Upload invalid YAML ----------
def test_upload_invalid_yaml(client):
    bad_yaml = b"{ this: [invalid: yaml"
    data = {
        'file': (io.BytesIO(bad_yaml), 'bad.yaml')
    }

    response = client.post('/upload-config', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert 'Invalid YAML' in response.get_json()['error']


# ---------- TEST: upload_if_new_config function ----------
def test_upload_if_new_config(tmp_path):
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text("source:\n  local:\n    path: 'mock.csv'")

    result = upload_if_new_config(str(yaml_file))
    assert "New config stored as version" in result or "Config already exists" in result
