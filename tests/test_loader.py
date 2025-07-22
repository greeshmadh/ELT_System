import os
import pytest
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from loader import read_yaml_config, load_csv_to_postgres

# Paths
CONFIG_PATH = "uploaded_configs/config.yaml"
CSV_PATH = "data/output_files/extracted_data.csv"

@pytest.fixture
def db_engine():
    config = read_yaml_config(CONFIG_PATH)
    db_cfg = config.get("target", {})
    engine_url = (
        f"postgresql+psycopg2://{db_cfg['user']}:{db_cfg['password']}@"
        f"{db_cfg['host']}:{db_cfg['port']}/{db_cfg['database']}"
    )
    return create_engine(engine_url)

def test_yaml_config_loads():
    config = read_yaml_config(CONFIG_PATH)
    assert isinstance(config, dict)
    assert "target" in config

def test_csv_file_exists():
    assert os.path.exists(CSV_PATH)

def test_load_csv_to_postgres(db_engine):
    config = read_yaml_config(CONFIG_PATH)
    db_cfg = config.get("target", {})
    table_name = db_cfg.get("table")

    # Load CSV
    load_csv_to_postgres(CSV_PATH, db_cfg, table_name)

    # Assert table exists
    inspector = inspect(db_engine)
    assert table_name in inspector.get_table_names()

    # Assert row count > 0
    with db_engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        row_count = result.scalar()
        assert row_count > 0

