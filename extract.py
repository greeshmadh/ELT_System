import os
import yaml
import logging
import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from pandas.api.types import is_dtype_equal
import json  

# ---------- CONFIG ----------
CONFIG_PATH = "./uploaded_configs/config_std_schema.yaml"
OUTPUT_FOLDER = "./data/output_files"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------- LOGGING SETUP ----------
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

# ---------- SCHEMA VALIDATION & STANDARDIZATION ----------
def validate_and_standardize(df, schema, strict_mode=False):
    try:
        # Use columns from schema if present
        columns = schema.get("columns", schema)
        # Rename columns to lowercase to avoid mismatches
        df.columns = df.columns.str.lower()
        # Ensure all schema columns exist in DataFrame
        for col in columns:
            if col not in df.columns:
                logging.error(f"Missing required column: {col}")
                return None
        # Only keep columns defined in schema if strict_mode is True
        if strict_mode:
            df = df[list(columns.keys())]
        return df
    except Exception as e:
        logging.error(f"Schema validation failed: {e}")
        return None

# ---------- LOCAL EXTRACTION ----------
def extract_from_local(path):
    data_frames = []
    if not os.path.exists(path):
        logging.error(f"Source path does not exist: {path}")
        return pd.DataFrame()

    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(full_path)
            elif filename.endswith('.json'):
                df = pd.read_json(full_path)
            elif filename.endswith('.txt'):
                df = pd.read_csv(full_path, delimiter='|')
            else:
                logging.warning(f"Unsupported file type skipped: {filename}")
                continue

            logging.info(f"Read {filename}, rows: {len(df)}")
            data_frames.append(df)

        except Exception as e:
            logging.error(f"Failed to read {filename}: {e}")

    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True)
        logging.info(f"Total combined rows from local: {len(combined_df)}")
        return combined_df
    else:
        logging.warning("No valid files found in local source.")
        return pd.DataFrame()

# ---------- API EXTRACTION ----------
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def extract_from_api(url, auth_token=None, folder_param=None):
    headers = {}
    if auth_token:
        headers["Authorization"] = auth_token

    params = {}
    if folder_param:
        params["path"] = folder_param

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    json_data = response.json()  # Parse response as JSON
    df = pd.DataFrame(json_data)
    logging.info(f"Extracted {len(df)} rows from API.")
    return df

# ---------- MAIN EXTRACTOR ----------
def run_extraction(config=None, output_csv_path=None, skip_api=False):
    if config is None:
        config = read_yaml_config(CONFIG_PATH)

    sources = config.get("sources", [])
    all_dataframes = []

    for source in sources:
        source_type = source.get("type")

        if source_type == "local":
            path = source.get("path")
            df_local = extract_from_local(path)
            if not df_local.empty:
                all_dataframes.append(df_local)

        elif source_type == "api" and not skip_api:
            url = source.get("url")
            auth_token = source.get("auth_token")
            folder_param = source.get("folder_param")
            df_api = extract_from_api(url, auth_token, folder_param)
            if not df_api.empty:
                all_dataframes.append(df_api)


        else:
            logging.warning(f"Unknown or skipped source type: {source_type}")


    # Combine all data
    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        logging.info("Combined data shape: %s", final_df.shape)

        # Check if schema exists in config
        schema = config.get("schema")
        strict_mode = config.get("strict_mode", False)
        if schema:
            validated_df = validate_and_standardize(final_df, schema,strict_mode)
            if validated_df is not None:
                validated_path = output_csv_path or os.path.join(OUTPUT_FOLDER, "extracted_data_std_schema.csv")
                validated_df.to_csv(validated_path, index=False)
                logging.info("Validated and standardized CSV written to extracted_data_std_schema.csv")
            else:
                logging.error("Schema validation failed. CSV not written.")
        else:
            raw_path = output_csv_path or os.path.join(OUTPUT_FOLDER, "extracted_data_std_schema.csv")
            final_df.to_csv(raw_path, index=False)
            logging.info(f"CSV written without schema validation to {raw_path}")


if __name__ == "__main__":
    run_extraction()
