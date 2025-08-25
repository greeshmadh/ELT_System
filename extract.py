import os
import yaml
import logging
import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from pandas.api.types import is_dtype_equal
import json  
import paramiko



# ---------- CONFIG ----------
CONFIG_PATH = "./uploaded_configs/sftp.yaml"
OUTPUT_FOLDER = "./data/output_files/s.csv"
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
        
        
        elif source_type == "sftp":
            df_sftp = extract_from_sftp(
            host=source["host"],
            port=source.get("port", 22),
            username=source["username"],
            password=source["password"],
            remote_path=source["path"],   # <-- your YAML uses "path", not "remote_path"
            local_path=output_csv_path or "./data/output_files/sftp.csv"
        )
        if not df_sftp.empty:
            all_dataframes.append(df_sftp)


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


def extract_from_sftp(host, port, username, password, remote_path, local_path):
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Download file
        sftp.get(remote_path, local_path)
        sftp.close()
        transport.close()

        # Read into DataFrame
        df = pd.read_csv(local_path)
        return df

    except Exception as e:
        print(f"SFTP extraction failed: {e}")
        return pd.DataFrame()



# def extract_from_sftp(host, port, username, password, remote_path, local_dir="./data/output_files"):
#     """
#     Download all CSV files from an SFTP folder and return as a single DataFrame.
#     """
#     try:
#         os.makedirs(local_dir, exist_ok=True)

#         logging.info(f"Connecting to SFTP server {host}:{port}")
#         transport = paramiko.Transport((host, port))
#         transport.connect(username=username, password=password)
#         sftp = paramiko.SFTPClient.from_transport(transport)

#         # List all files in remote_path
#         file_list = sftp.listdir(remote_path)
#         logging.info(f"Found {len(file_list)} files in {remote_path}")

#         all_dfs = []
#         for file_name in file_list:
#             if file_name.endswith(".csv"):
#                 remote_file = os.path.join(remote_path, file_name)
#                 local_file = os.path.join(local_dir, file_name)
#                 logging.info(f"Downloading {remote_file} to {local_file}")
#                 sftp.get(remote_file, local_file)
#                 df = pd.read_csv(local_file)
#                 all_dfs.append(df)

#         sftp.close()
#         transport.close()

#         if all_dfs:
#             combined_df = pd.concat(all_dfs, ignore_index=True)
#             logging.info(f"Combined DataFrame shape: {combined_df.shape}")
#             return combined_df
#         else:
#             logging.warning("No CSV files found in SFTP directory.")
#             return pd.DataFrame()

#     except Exception as e:
#         logging.error(f"SFTP extraction failed: {e}")
#         return pd.DataFrame()




if __name__ == "__main__":
    run_extraction()
