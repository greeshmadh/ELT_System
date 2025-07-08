from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
from extract import run_extraction  # my extraction logic
from loader import load_csv_to_postgres, read_yaml_config #my loader logic


app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

CONFIG_PATH = "config.yaml"
CSV_PATH = "extracted_data.csv"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def scheduled_elt_job():
    logging.info(f"[{datetime.now()}] Running scheduled ELT job...")
    
    # Run extraction
    run_extraction()

    # Load to DB
    config = read_yaml_config(CONFIG_PATH)
    target_config = config.get("target", {})
    if target_config.get("type") == "postgres":
        load_csv_to_postgres(CSV_PATH, target_config, target_config.get("table", "raw_data"))
    else:
        logging.error("No valid target DB config found.")

@app.route('/schedule-job', methods=['POST'])
def schedule_job():
    """Schedules a job to run every 1 hours."""
    scheduler.add_job(scheduled_elt_job, 'interval', hours=1, id='elt_job', replace_existing=True)
    return jsonify({"message": "ELT job scheduled to run every 1 hours"}), 200

# @app.route('/unschedule-job', methods=['POST'])
# def unschedule_job():
#     """Cancels the job."""
#     scheduler.remove_job('elt_job')
#     return jsonify({"message": "Scheduled ELT job cancelled"}), 200

@app.route('/')
def health_check():
    return jsonify({"status": "Scheduler API running"}), 200

if __name__ == "__main__":
    app.run(debug=True)
