import os
import pandas as pd
import yaml
import logging
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, Float, Text
from sqlalchemy.exc import ProgrammingError
from tenacity import retry, stop_after_attempt, wait_exponential

# ---------- CONFIG ----------
CONFIG_PATH = "uploaded_configs/config.yaml"
CSV_PATH = "data/output_files/extracted_data.csv"

# ---------- LOGGING ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ---------- YAML CONFIG LOADER ----------
def read_yaml_config(path):
    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        logging.info("YAML config loaded successfully.")
        return config
    except Exception as e:
        logging.error(f"Error reading YAML config: {e}")
        return {}

# ---------- Infer SQLAlchemy Column Types ----------
def infer_sqlalchemy_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return Integer
    elif pd.api.types.is_float_dtype(dtype):
        return Float
    elif pd.api.types.is_string_dtype(dtype):
        return Text
    else:
        return String

# ---------- Table Creation ----------
def create_table_from_df(engine, df, table_name):
    metadata = MetaData()
    columns = []

    for col in df.columns:
        col_type = infer_sqlalchemy_type(df[col].dtype)
        columns.append(Column(col, col_type))

    table = Table(table_name, metadata, *columns)
    metadata.create_all(engine, checkfirst=True)
    logging.info(f"Table '{table_name}' created or already exists.")

# ---------- LOAD FUNCTION ----------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10))
def load_csv_to_postgres(csv_path, db_config, table_name):
    df = pd.read_csv(csv_path)
    logging.info(f"CSV loaded with {len(df)} rows and columns: {list(df.columns)}")

    engine_url = (
        f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    engine = create_engine(engine_url)

    create_table_from_df(engine, df, table_name)
    df.to_sql(table_name, engine, if_exists='append', index=False)
    logging.info(f"Data successfully loaded into table '{table_name}'.")

# ---------- ENTRY POINT ----------
if __name__ == "__main__":
    config = read_yaml_config(CONFIG_PATH)
    target_config = config.get("target", {})

    if target_config.get("type") == "postgres":
        load_csv_to_postgres(CSV_PATH, target_config, target_config.get("table", "load_data"))
    else:
        logging.error("Invalid or missing PostgreSQL target configuration.")
