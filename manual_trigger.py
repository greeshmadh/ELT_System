# from flask import Flask, jsonify
# from extract import run_extraction  # my extract function
# from loader import load_csv_to_postgres, read_yaml_config  # my loader + config reader
# import logging

# app = Flask(__name__)

# CONFIG_PATH = "./uploaded_configs/config_std_schema.yaml"
# CSV_PATH = "./data/output_files/extracted_data_std_schema.csv"

# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# @app.route('/trigger-job', methods=['POST'])
# def trigger_elt_job():
#     try:
#         logging.info("Manual ELT job trigger initiated...")

#         # Step 1: Run Extraction
#         run_extraction(skip_api=True)

#         # Step 2: Load extracted CSV into PostgreSQL
#         config = read_yaml_config(CONFIG_PATH)
#         target_config = config.get("target", {})
#         table_name = target_config.get("table", "raw_data")

#         # Step 1: Run Extraction with config and expected CSV output
#         run_extraction(config=config, output_csv_path=CSV_PATH, skip_api=True)

#         # Step 2: Load to DB
#         if target_config.get("type") == "postgres":
#             load_csv_to_postgres(CSV_PATH, target_config, table_name)
#         else:
#             return jsonify({"error": "Invalid target config"}), 400

#         logging.info("Manual ELT job completed.")
#         return jsonify({"message": "ELT job triggered and completed successfully."}), 200

#     except Exception as e:
#         logging.error(f"Manual ELT job failed: {e}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/')
# def health_check():
#     return jsonify({"status": "Manual trigger API is running"}), 200

# if __name__ == '__main__':
#     app.run(debug=True, port=5050)


from flask import Flask, jsonify
from extract import run_extraction, read_yaml_config
from loader import load_csv_to_postgres
import logging
import os
import pandas as pd
import time
import threading
import hashlib

app = Flask(__name__)

CONFIG_PATH = "./uploaded_configs/config.yaml"
CSV_PATH = "./data/output_files/extracted_data.csv"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

inserted_hashes = set()  # to track inserted row hashes


def hash_row(row):
    return hashlib.sha256(str(row.values).encode()).hexdigest()


def extract_and_load(config):
    # Run extraction
    run_extraction(config=config, output_csv_path=CSV_PATH, skip_api=True)
    df = pd.read_csv(CSV_PATH)

    # Deduplicate: filter out rows already in DB using hash
    new_rows = df[~df.apply(lambda row: hash_row(row) in inserted_hashes, axis=1)]

    if not new_rows.empty:
        # Append hashes
        for _, row in new_rows.iterrows():
            inserted_hashes.add(hash_row(row))

        # Load only new rows to DB
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
    logging.info("Started background watcher for changes in input folder...")
    while True:
        try:
            extract_and_load(config)
        except Exception as e:
            logging.error(f"Watcher failed: {e}")
        time.sleep(60)  # check every 1 minute


@app.route('/trigger-job', methods=['POST'])
def trigger_elt_job():
    try:
        logging.info("Manual ELT job trigger initiated...")

        config = read_yaml_config(CONFIG_PATH)

        # Phase 1: initial full extraction & DB load
        extract_and_load(config)

        # Phase 2: start background watcher
        thread = threading.Thread(target=background_watcher, args=(config,))
        thread.daemon = True
        thread.start()

        return jsonify({"message": "ELT job started and background watcher running."}), 200

    except Exception as e:
        logging.error(f"Manual ELT job failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/')
def health_check():
    return jsonify({"status": "Manual trigger API is running"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5050)
