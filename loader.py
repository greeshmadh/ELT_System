import pandas as pd
import yaml
import logging
from sqlalchemy import create_engine
from tenacity import retry, stop_after_attempt, wait_exponential

# ---------- CONFIG ----------
CONFIG_PATH = "config.yaml"
CSV_PATH = "extracted_data.csv"

# ---------- LOGGING ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ---------- YAML LOADER ----------
def read_yaml_config(path):
    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        logging.info("YAML config loaded successfully.")
        return config
    except Exception as e:
        logging.error(f"Error reading YAML config: {e}")
        return {}

# ---------- LOAD FUNCTION ----------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10))
def load_csv_to_postgres(csv_path, db_config, table_name):
    df = pd.read_csv(csv_path)
    logging.info(f"CSV loaded with {len(df)} rows")

    engine_url = (
        f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    engine = create_engine(engine_url)#initializes a connection engine that SQLAlchemy can use to interact with the PostgreSQL database.



    df.to_sql(table_name, engine, if_exists='append', index=False)
    logging.info(f"Data successfully loaded into table '{table_name}'")

# ---------- RUN ----------
if __name__ == "__main__":
    config = read_yaml_config(CONFIG_PATH)
    target_config = config.get("target", {})

    if target_config.get("type") == "postgres":
        load_csv_to_postgres(CSV_PATH, target_config, target_config.get("table", "load_data"))#default-load_data
    else:
        logging.error("Invalid or missing PostgreSQL target configuration.")
