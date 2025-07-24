import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from extract import (
    extract_from_local,
    extract_from_api,
    validate_and_standardize,
    run_extraction,
    read_yaml_config
)

# Define test data directory and ensure it exists
TEST_LOCAL_DIR = './tests/test_data'
os.makedirs(TEST_LOCAL_DIR, exist_ok=True)

# Create a mock CSV file to test local extraction
sample_csv_path = os.path.join(TEST_LOCAL_DIR, 'sample.csv')
pd.DataFrame({'id': [1, 2], 'name': ['Alice', 'Bob']}).to_csv(sample_csv_path, index=False)


# Test extracting data from a valid local path
def test_extract_from_local_valid():
    df = extract_from_local(TEST_LOCAL_DIR)
    assert not df.empty                 # Data should not be empty
    assert 'id' in df.columns          # Check expected column exists


# Test extracting from an invalid directory
def test_extract_from_local_invalid_path():
    df = extract_from_local('./invalid/path')
    assert df.empty                   # Should return empty DataFrame


# Mock API response and test API-based extraction
@patch('extract.requests.get')
def test_extract_from_api_mock(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'id': 1, 'value': 'abc'}]
    mock_get.return_value = mock_response

    df = extract_from_api("http://fakeapi.com/data")
    assert not df.empty              # Response should return data
    assert 'value' in df.columns    # Ensure API field exists


# Test validation passes with matching schema
def test_validate_and_standardize_pass():
    df = pd.DataFrame({'id': [1], 'name': ['Alice'], 'age': [25]})
    schema = {'columns': {'id': 'int', 'name': 'str', 'age': 'int'}}
    result = validate_and_standardize(df, schema)
    assert result is not None
    assert list(result.columns) == ['id', 'name', 'age']


# Test validation fails if schema columns are missing
def test_validate_and_standardize_missing_column():
    df = pd.DataFrame({'id': [1], 'name': ['Alice']})  # 'age' missing
    schema = {'columns': {'id': 'int', 'name': 'str', 'age': 'int'}}
    result = validate_and_standardize(df, schema)
    assert result is None


# Smoke test for running full extraction from local to CSV
def test_run_extraction_smoke(tmp_path):
    config = {
        'sources': [
            {'type': 'local', 'path': TEST_LOCAL_DIR}
        ],
        'schema': {
            'columns': {'id': 'int', 'name': 'str'}
        },
        'strict_mode': True
    }

    output_path = tmp_path / "output.csv"
    run_extraction(config=config, output_csv_path=str(output_path))
    assert output_path.exists()      # Output file should be created


# Test reading a valid YAML file
def test_read_yaml_valid(tmp_path):
    file = tmp_path / "test.yaml"
    file.write_text("source:\n  local:\n    path: 'data.csv'")
    result = read_yaml_config(file)
    assert "source" in result         
