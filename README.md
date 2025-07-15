# ELT Pipeline Project

This project implements a complete ELT (Extract, Load, Transform) pipeline with support for:

- Local and API-based data extraction
- YAML configuration management with versioning
- Schema validation and standardization
- PostgreSQL loading
- Manual and scheduled ELT job triggering
- Frontend integration-ready endpoints for configuration upload

---

## Features

### 1. **Data Extraction**
- **Local Extraction**: Supports reading `.csv`, `.json`, and `.txt` files from a specified folder.
- **API Extraction**: Fetches JSON data from an API endpoint using optional authentication tokens.
- **Combined Output**: All extracted data is concatenated into one DataFrame and written to CSV.
- Automatically re-extracts all files on change detection during monitoring.


### 2. **YAML Configuration**
- Configuration is managed through a `config.yaml` file.
- Defines data sources (`local`, `api`) and target PostgreSQL DB credentials.
- Optional `schema` section defines expected column names and types.
- Supports `strict_mode` for schema validation.
- You can optionally define:
  - `start_time`: when the ELT job should start (format: `YYYY-MM-DD HH:MM`)
  - `end_time`: when the job should stop (monitoring ends)


### 3. **Schema Validation**
- If a schema is provided in the YAML, all incoming data is validated against it.
- Supports type standardization (e.g., converting strings to integers).
- In strict mode, only columns in the schema are retained.

### 4. **PostgreSQL Data Load**
- Loads validated CSV into PostgreSQL using SQLAlchemy.
- Table is created automatically if it doesn’t exist.
- Appends data to the specified target table.
- Supports retry mechanism for fault-tolerance.
- Only new rows are inserted using a row-level hash to prevent duplicates.


### 5. **YAML Upload and Versioning**
- Endpoint: `POST /upload-config`
- Accepts YAML files and stores them in a `config_history` table in the database.
- Automatically increments version number.
- Validates YAML syntax before storing.

### 6. **Manual & Scheduled ELT Trigger with Monitoring**
- Script: `manual_trigger.py`
- Supports two modes:
  1. **Manual Mode**: 
     - Run directly with or without a config file:
       ```bash
       python manual_trigger.py
       python manual_trigger.py ./uploaded_configs/my_config.yaml
       ```
     - Triggers the ELT job immediately.
     - Starts background monitoring to check for file changes every 60 seconds.
     - Press `g` + Enter in terminal to stop the job gracefully.

  2. **Scheduled Mode (YAML-based)**:
     - The same script reads `start_time` and `end_time` from YAML:
       ```yaml
       start_time: "2025-07-15 19:00"
       end_time: "2025-07-15 19:15"
       ```
     - It waits until `start_time` to begin the ELT job.
     - Stops automatically at `end_time`.
- Deduplicates rows using row-level hashing.
- Automatically overwrites CSV and loads only new data to the database.

### 8. **Logging and Retry**
- Retry decorators for API and DB operations (up to 3 attempts).
- Structured logging for all major steps.


Dependencies

Python 3.8+

pandas

Flask

SQLAlchemy

psycopg2

requests

tenacity

PyYAML

APScheduler

watchdog

hashlib (built-in)



