import logger
import os
import threading
import time
import hashlib
import pandas as pd
from datetime import datetime
import sys

from extract import run_extraction, read_yaml_config
from loader import load_csv_to_postgres
from config_manager import upload_if_new_config
from logger import logger

# Set config and output file paths
CONFIG_PATH = sys.argv[1] if len(sys.argv) > 1 else "./uploaded_configs/SFTP.yaml"
CSV_PATH = "./data/output_files/sftp_final1.csv"

# Store inserted row hashes to avoid duplication
inserted_hashes = set()

# Flag to signal stopping of background job
stop_flag = threading.Event()


# Generate a unique hash for each row (used for deduplication)
def hash_row(row):
    return hashlib.sha256(str(row.values).encode()).hexdigest()


# Extract data, filter new rows, and load to DB
def extract_and_load(config):
    run_extraction(config=config, output_csv_path=CSV_PATH, skip_api=True)
    df = pd.read_csv(CSV_PATH)

    # Filter only new rows not already inserted
    new_rows = df[~df.apply(lambda row: hash_row(row) in inserted_hashes, axis=1)]

    if not new_rows.empty:
        for _, row in new_rows.iterrows():
            inserted_hashes.add(hash_row(row))  # Add new hashes to memory

        target_config = config.get("target", {})
        table_name = target_config.get("table", "raw_data")

        # Load new data into the database
        if target_config.get("type") == "postgres":
            temp_csv_path = "./data/output_files/temp_upload.csv"
            new_rows.to_csv(temp_csv_path, index=False)
            load_csv_to_postgres(temp_csv_path, target_config, table_name)
            os.remove(temp_csv_path)
            logger.info(f"Loaded {len(new_rows)} new rows to DB.")
        else:
            logger.error("Invalid DB config.")
    else:
        logger.info("No new rows to load.")


# Background thread function that checks for new data every 60 seconds
def background_watcher(config):
    logger.info("Started background watcher. Checking for updates every 60 seconds.")
    while not stop_flag.is_set():
        try:
            extract_and_load(config)
        except Exception as e:
            logger.error(f"Watcher failed: {e}")
        time.sleep(60)


#Thread for manual stop by entering 'g'
def wait_for_manual_stop():
    logger.info("Press 'g' then Enter to gracefully stop the job.")
    while not stop_flag.is_set():
        user_input = input().strip().lower()
        if user_input == 'g':
            logger.info("Graceful shutdown signal received.")
            stop_flag.set()
            return True


# Main function
def main():
    logger.info("Reading config from: %s", CONFIG_PATH)
    config = read_yaml_config(CONFIG_PATH)

    # Store config in DB if it's new
    try:
        upload_status = upload_if_new_config(CONFIG_PATH)
        logger.info(upload_status)
    except Exception as e:
        logger.warning(f"Could not upload YAML config: {e}")

    # Handle start time (delay start until configured time)
    start_time_str = config.get("start_time")
    end_time_str = config.get("end_time")

    if start_time_str:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
        while datetime.now() < start_time:
            logger.info(f"Waiting for start time: {start_time}")
            time.sleep(10)

    logger.info("Starting ELT job...")
    extract_and_load(config)

    # Start background thread for continuous checking
    watcher_thread = threading.Thread(target=background_watcher, args=(config,))
    watcher_thread.start()

    # Optional thread for manual 'g' input
    if sys.stdin.isatty():
        input_thread = threading.Thread(target=wait_for_manual_stop)
        input_thread.start()

    # If end_time specified, auto-stop job
    if end_time_str:
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
        while datetime.now() < end_time and not stop_flag.is_set():
            time.sleep(5)
        logger.info(f"End time {end_time} reached. Stopping job...")
        stop_flag.set()

    watcher_thread.join()
    logger.info("ELT job completed and stopped.")


# Entry point
if __name__ == "__main__":
    main()
