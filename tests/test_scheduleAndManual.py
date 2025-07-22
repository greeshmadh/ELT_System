import pytest
import pandas as pd
from unittest.mock import patch
from scheduleAndManual import hash_row, extract_and_load, inserted_hashes

# Sample config
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

@pytest.fixture
def dummy_df():
    return pd.DataFrame({
        "id": [1, 2],
        "name": ["Alice", "Bob"]
    })

def test_hash_row_is_consistent(dummy_df):
    row = dummy_df.iloc[0]
    assert isinstance(hash_row(row), str)
    assert len(hash_row(row)) == 64
    assert hash_row(row) == hash_row(row)

@patch("scheduleAndManual.run_extraction")
@patch("scheduleAndManual.load_csv_to_postgres")
@patch("scheduleAndManual.pd.read_csv")
def test_extract_and_load_new_data(mock_read_csv, mock_loader, mock_extractor):
    df = pd.DataFrame({"id": [100], "name": ["Test"]})
    mock_read_csv.return_value = df

    # Clear hash set to allow insert
    inserted_hashes.clear()
    
    extract_and_load(SAMPLE_CONFIG)
    mock_loader.assert_called_once()
    args, _ = mock_loader.call_args
    assert args[2] == "sample_table"

@patch("scheduleAndManual.run_extraction")
@patch("scheduleAndManual.load_csv_to_postgres")
@patch("scheduleAndManual.pd.read_csv")
def test_extract_and_load_duplicates_skipped(mock_read_csv, mock_loader, mock_extractor):
    df = pd.DataFrame({"id": [999], "name": ["Duplicate"]})
    mock_read_csv.return_value = df

    inserted_hashes.clear()
    extract_and_load(SAMPLE_CONFIG)  # first insert
    extract_and_load(SAMPLE_CONFIG)  # second should skip

    assert mock_loader.call_count == 1
