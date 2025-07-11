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

### 6. **Manual ELT Trigger with Continuous Monitoring**
- Endpoint: `POST /trigger-job`
- Triggers the full ELT pipeline:
  - Extracts all current files.
  - Validates and standardizes based on schema (if provided).
  - Overwrites CSV output.
  - Loads all rows to PostgreSQL (creating table if necessary).
- Then continuously monitors the input folder every 1 minute:
  - If new or modified files are detected:
    - Overwrites the CSV with fresh combined data.
    - Detects and loads only **new, previously unseen rows** to the database.
- Uses a background thread to perform this monitoring.
- Deduplicates rows using a secure hash mechanism to avoid repeated inserts.


### 7. **Scheduled ELT Job**
- Endpoint: `POST /schedule-job`
- Schedules the ELT job to run every hour using APScheduler.
- Supports auto-replacement of existing scheduled jobs.

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



