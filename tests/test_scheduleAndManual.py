import pytest
import pandas as pd
from unittest.mock import patch
from scheduleAndManual import hash_row, extract_and_load, inserted_hashes
from scheduleAndManual import wait_for_manual_stop, background_watcher
import threading
import time
from scheduleAndManual import stop_flag
from extract import read_yaml_config

# Test background watcher exits immediately when stop_flag is already set
def test_background_watcher_runs(tmp_path):
    # Create a mock config file
    config_path = tmp_path / "mock_config.yaml"
    config_path.write_text("source:\n  local:\n    path: 'mock.csv'")
    config = read_yaml_config(config_path)

    stop_flag.set()  # Prevent actual loop by pre-setting stop
    t = threading.Thread(target=background_watcher, args=(config,))
    t.start()
    t.join()
    assert not t.is_alive()  


# Sample config used for extraction tests
SAMPLE_CONFIG = {
    "target": {
        "type": "postgres",
        "user": "user",
        "password": "pass",
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "table": "sample_table"
    }
}

# Fixture to provide dummy DataFrame
@pytest.fixture
def dummy_df():
    return pd.DataFrame({
        "id": [1, 2],
        "name": ["Alice", "Bob"]
    })

# Test hashing function for consistency and SHA-256 output
def test_hash_row_is_consistent(dummy_df):
    row = dummy_df.iloc[0]
    assert isinstance(hash_row(row), str)        # Should return a string
    assert len(hash_row(row)) == 64              # SHA-256 is 64 hex characters
    assert hash_row(row) == hash_row(row)        # Hashing same row gives same result


# Test that extract_and_load works and calls loader when data is new
@patch("scheduleAndManual.run_extraction")
@patch("scheduleAndManual.load_csv_to_postgres")
@patch("scheduleAndManual.pd.read_csv")
def test_extract_and_load_new_data(mock_read_csv, mock_loader, mock_extractor):
    df = pd.DataFrame({"id": [100], "name": ["Test"]})
    mock_read_csv.return_value = df

    inserted_hashes.clear()  # Ensure it's empty for clean insert

    extract_and_load(SAMPLE_CONFIG)

    # Loader should be called with expected table name
    mock_loader.assert_called_once()
    args, _ = mock_loader.call_args
    assert args[2] == "sample_table"


# Test that extract_and_load skips duplicates already hashed
@patch("scheduleAndManual.run_extraction")
@patch("scheduleAndManual.load_csv_to_postgres")
@patch("scheduleAndManual.pd.read_csv")
def test_extract_and_load_duplicates_skipped(mock_read_csv, mock_loader, mock_extractor):
    df = pd.DataFrame({"id": [999], "name": ["Duplicate"]})
    mock_read_csv.return_value = df

    inserted_hashes.clear()

    # First insert should be processed
    extract_and_load(SAMPLE_CONFIG)

    # Second time with same data should be skipped
    extract_and_load(SAMPLE_CONFIG)

    assert mock_loader.call_count == 1  # Loader should be called only once
