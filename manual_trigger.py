from flask import Flask, jsonify
from extract import run_extraction  # my extract function
from loader import load_csv_to_postgres, read_yaml_config  # my loader + config reader
import logging

app = Flask(__name__)

CONFIG_PATH = "config.yaml"
CSV_PATH = "extracted_data.csv"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.route('/trigger-job', methods=['POST'])
def trigger_elt_job():
    try:
        logging.info("Manual ELT job trigger initiated...")

        # Step 1: Run Extraction
        run_extraction(skip_api=True)

        # Step 2: Load extracted CSV into PostgreSQL
        config = read_yaml_config(CONFIG_PATH)
        target_config = config.get("target", {})
        table_name = target_config.get("table", "raw_data")

        if target_config.get("type") == "postgres":
            load_csv_to_postgres(CSV_PATH, target_config, table_name)
        else:
            return jsonify({"error": "Invalid target config"}), 400

        logging.info("Manual ELT job completed.")
        return jsonify({"message": "ELT job triggered and completed successfully."}), 200

    except Exception as e:
        logging.error(f"Manual ELT job failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def health_check():
    return jsonify({"status": "Manual trigger API is running"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5050)
