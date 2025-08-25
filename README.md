# ELT Pipeline Project

This project implements a complete ELT (Extract, Load, Transform) pipeline with support for:

- Local data extraction
- SFTP file extraction
- YAML configuration management with versioning
- Schema validation and standardization
- PostgreSQL loading
- Manual and scheduled ELT job triggering
- Frontend integration:-
  - Admin:- Upload yaml, schedule and trigger elt job, view loaded data, view backend coverage test result, view
            config history
  - User:- View loaded data, view backend coverage test result,upload yaml file.

-----

## Features

### 1. **Data Extraction**
- **Local Extraction**: Supports reading `.csv`, `.json`, and `.txt` files from a specified folder.
- **API Extraction**: Fetches JSON data from an API endpoint using optional authentication tokens.
- **Combined Output**: All extracted data is concatenated into one DataFrame and written to CSV.
- Automatically re-extracts all files on change detection during monitoring.

### 1.0 **SFTP Extraction Support**
- Implemented sftp server via docker 
    docker run -p 2222:22 -d atmoz/sftp foo:pass:::upload
    Next time start here :
      sftp -P 2222 foo@localhost
      put your_test.csv /upload/sample.csv
    This uploads a file to the sftp server. 
- Added ability to connect to an SFTP server via credentials provided in YAML.
- Supports downloading:
  - A **single CSV file** (remote path points to file)
- Automatically combines downloaded CSVs into a single DataFrame.
- Saves results directly to the configured `output_csv_path`
- **Run along with Local extraction**

**YAML Example for Single File:**
```yaml
sources:
  - type: sftp
    sftp:
      host: "localhost"
      port: 2222
      username: "foo"
      password: "pass"
      remote_path: "/upload/sample.csv"



### 2. **YAML Configuration**
- Configuration is managed through a `config.yaml` file.
- Defines data sources (`local`, `api`) and target PostgreSQL DB credentials.
- Optional `schema` section defines expected column names and types.
- Supports `strict_mode` for schema validation. If 'True' follows the mentioned schema else loads all data rows.
- You can optionally define:
  - `start_time`: when the ELT job should start (format: `YYYY-MM-DD HH:MM`)
  - `end_time`: when the job should stop (monitoring ends)


### 3. **Schema Validation**
- If a schema is provided in the YAML, all incoming data is validated against it.
- In strict mode, only columns in the schema are retained.

### 4. **PostgreSQL Data Load**
- Loads validated CSV into PostgreSQL using SQLAlchemy.
- Table is created automatically if it doesn’t exist.
- Table name is dynamically read from the uploaded YAML file.
- Appends data to the specified(in yaml) target table.
- Supports retry mechanism for fault-tolerance.
- Only new rows are inserted using a row-level hash to prevent duplicates.
- If yaml previously uploaded and data from sources not changed then no new data(duplicates) is added.
- Users can preview database table content before running the ELT job using a YAML config.

### 5. **YAML Upload and Versioning**
- Endpoint: `POST /upload-config`
- Accepts YAML files and stores them in a `config_history` table in the database.
- Automatically increments version number.
- Validates YAML syntax before storing.
- If yaml already exists in table doesn't upload but uses the same. 

### 6. **Manual & Scheduled ELT Trigger with Monitoring**
- Script: `scheduleAndManual.py`
- Supports two modes:
  1. **Manual Mode**: 
     - Run directly with or without schedule times.
     - Triggers the ELT job immediately.
     - Starts background monitoring to check for file changes every 60 seconds.
     - Press `g` + Enter in terminal to stop the job gracefully.

  2. **Scheduled Mode (YAML-based)**:
     - The same script reads `start_time` and `end_time` from YAML:
     - It waits until `start_time` to begin the ELT job.
     - Stops automatically at `end_time`.

- Deduplicates rows using row-level hashing.
- Automatically overwrites CSV and loads only new data to the database.

### 7. **Retry**
- Retry decorators for API and DB operations (up to 3 attempts).

### 8. **JWT Authentication**

- `/auth/login` issues JWT tokens for **admin** and **user** roles.
- Protected endpoints use `@jwt_required()` decorator in Flask.
- JWT token is sent with each request in the `Authorization: Bearer <token>` header.

### 9. **Admin Dashboard (Angular Frontend)**

Provides a web-based UI to manage the ELT pipeline.

  ### Features:

  - **Trigger ELT Job** by uploading a YAML configuration file.
  - **View Logs** – shows the latest 100 lines from `elt.log` where the logs are saved.
  - **View Config Upload History** – shows versioned YAML uploads.
  - Requires login via frontend using valid credentials.
  - Stores JWT securely in `localStorage` for authorized requests.
  - **View Table Data:** Admin can upload a YAML file to view what data is currently present in the target PostgreSQL table.
  - **View backend test coverage percentage**.


### 10. Log Monitoring

- **Endpoint**: `GET /logs`
- Returns the **last 100 lines** from the ELT log file (`elt.log`).
- Used in the frontend to show real-time monitoring (with auto-refresh every 10 seconds).
- Log entries include:
  - Timestamp
  - ELT Job status
  - Error messages


### 11. YAML Upload History UI

- View complete YAML configurations data that have been uploaded and versioned.
- Configs are stored in the `config_history` table in PostgreSQL.

### Displayed Info:

-  **ID**
- **Version**
- **Timestamp**
- **YAML Preview** (first 100 characters)
- **View Button** to load full YAML content 

### 12. User Dashboard (Angular Frontend)

A simplified dashboard tailored for **non-admin users**.

### Features:

- **Upload YAML** to view data present in the target PostgreSQL table.
- **Authenticated** via JWT token using the `user` role.
- **Reuses** the same `/data-view` backend logic used by the admin.
- Helps users verify table contents before running the ELT job.
- **View backend test coverage report** percantage and progress bar for visual.

> Ideal for analysts or data consumers who need visibility but not full ELT control.

### 13. Test Coverage Report

- A backend route `/coverage-report` serves the parsed JSON coverage summary.
- The coverage report includes:
  - Total covered lines
  - Total statements
  - Percentage of code covered by tests
- Helps developers ensure that **critical backend logic** is well tested and maintained.

-----


## Dependencies:-

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

paramiko



