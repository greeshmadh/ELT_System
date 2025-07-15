import logging
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

CONFIG_PATH = sys.argv[1] if len(sys.argv) > 1 else "./uploaded_configs/testing.yaml"
CSV_PATH = "./data/output_files/schedule.csv"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

inserted_hashes = set()
stop_flag = threading.Event()


def hash_row(row):
    return hashlib.sha256(str(row.values).encode()).hexdigest()


def extract_and_load(config):
    run_extraction(config=config, output_csv_path=CSV_PATH, skip_api=True)
    df = pd.read_csv(CSV_PATH)

    new_rows = df[~df.apply(lambda row: hash_row(row) in inserted_hashes, axis=1)]
    if not new_rows.empty:
        for _, row in new_rows.iterrows():
            inserted_hashes.add(hash_row(row))

        target_config = config.get("target", {})
        table_name = target_config.get("table", "raw_data")

        if target_config.get("type") == "postgres":
            temp_csv_path = "./data/output_files/temp_upload.csv"
            new_rows.to_csv(temp_csv_path, index=False)
            load_csv_to_postgres(temp_csv_path, target_config, table_name)
            os.remove(temp_csv_path)
            logging.info(f"Loaded {len(new_rows)} new rows to DB.")
        else:
            logging.error("Invalid DB config.")
    else:
        logging.info("No new rows to load.")


def background_watcher(config):
    logging.info("Started background watcher. Checking for updates every 60 seconds.")
    while not stop_flag.is_set():
        try:
            extract_and_load(config)
        except Exception as e:
            logging.error(f"Watcher failed: {e}")
        time.sleep(60)


def wait_for_manual_stop():
    logging.info("Press 'g' then Enter to gracefully stop the job.")
    while not stop_flag.is_set():
        user_input = input().strip().lower()
        if user_input == 'g':
            logging.info("Graceful shutdown signal received.")
            stop_flag.set()
            break


def main():
    logging.info("Reading config from: %s", CONFIG_PATH)
    config = read_yaml_config(CONFIG_PATH)

    # Upload config if it's new
    try:
        upload_status = upload_if_new_config(CONFIG_PATH)
        logging.info(upload_status)
    except Exception as e:
        logging.warning(f"Could not upload YAML config: {e}")

    start_time_str = config.get("start_time")
    end_time_str = config.get("end_time")

    if start_time_str:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
        while datetime.now() < start_time:
            logging.info(f"Waiting for start time: {start_time}")
            time.sleep(10)

    logging.info("Starting ELT job...")
    extract_and_load(config)

    # Start watcher
    watcher_thread = threading.Thread(target=background_watcher, args=(config,))
    watcher_thread.start()

    # If manual, allow 'g' input to stop
    if sys.stdin.isatty():
        input_thread = threading.Thread(target=wait_for_manual_stop)
        input_thread.start()

    if end_time_str:
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
        while datetime.now() < end_time and not stop_flag.is_set():
            time.sleep(5)
        logging.info(f"End time {end_time} reached. Stopping job...")
        stop_flag.set()

    watcher_thread.join()
    logging.info("ELT job completed and stopped.")


if __name__ == "__main__":
    main()
