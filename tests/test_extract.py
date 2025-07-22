import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from extract import (
    extract_from_local,
    extract_from_api,
    validate_and_standardize,
    run_extraction
)

# Sample test data directory
TEST_LOCAL_DIR = './tests/test_data'
os.makedirs(TEST_LOCAL_DIR, exist_ok=True)

# Create a sample CSV file for testing
sample_csv_path = os.path.join(TEST_LOCAL_DIR, 'sample.csv')
pd.DataFrame({'id': [1, 2], 'name': ['Alice', 'Bob']}).to_csv(sample_csv_path, index=False)


def test_extract_from_local_valid():
    df = extract_from_local(TEST_LOCAL_DIR)
    assert not df.empty
    assert 'id' in df.columns


def test_extract_from_local_invalid_path():
    df = extract_from_local('./invalid/path')
    assert df.empty


@patch('extract.requests.get')
def test_extract_from_api_mock(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'id': 1, 'value': 'abc'}]
    mock_get.return_value = mock_response

    df = extract_from_api("http://fakeapi.com/data")
    assert not df.empty
    assert 'value' in df.columns


def test_validate_and_standardize_pass():
    df = pd.DataFrame({'id': [1], 'name': ['Alice'], 'age': [25]})
    schema = {'columns': {'id': 'int', 'name': 'str', 'age': 'int'}}
    result = validate_and_standardize(df, schema)
    assert result is not None
    assert list(result.columns) == ['id', 'name', 'age']


def test_validate_and_standardize_missing_column():
    df = pd.DataFrame({'id': [1], 'name': ['Alice']})  # missing 'age'
    schema = {'columns': {'id': 'int', 'name': 'str', 'age': 'int'}}
    result = validate_and_standardize(df, schema)
    assert result is None


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
    assert output_path.exists()
