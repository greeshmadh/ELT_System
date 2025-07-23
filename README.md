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
-Users can now preview database table content before running the ELT job using a YAML config.
-Table name is dynamically read from the uploaded YAML file.


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

## 🔐 7. JWT Authentication

- `/auth/login` issues JWT tokens for **admin** and **user** roles.
- Protected endpoints use `@jwt_required()` decorator in Flask.
- JWT token is sent with each request in the `Authorization: Bearer <token>` header.

---

## 🖥️ 9. Admin Dashboard (Angular Frontend)

Provides a web-based UI to manage the ELT pipeline.

### Features:

- ✅ **Trigger ELT Job** by uploading a YAML configuration file.
- 📄 **View Logs** – shows the latest 100 lines from `elt.log`.
- 📜 **View Config Upload History** – shows versioned YAML uploads.
- 🔐 Requires login via frontend using valid credentials.
- 💾 Stores JWT securely in `localStorage` for authorized requests.
-📊 View Table Data: Admin can upload a YAML file to view what data is currently present in the target PostgreSQL table.

---

## 📄 10. Log Monitoring

- **Endpoint**: `GET /logs`
- Returns the **last 100 lines** from the ELT log file (`elt.log`).
- Used in the frontend to show real-time monitoring (with auto-refresh every 5 seconds).
- Log entries include:
  - Timestamp
  - ELT Job status
  - Error messages

---

## 📝 11. YAML Upload History UI

- View YAML configurations that have been uploaded and versioned.
- Configs are stored in the `config_history` table in PostgreSQL.

### Displayed Info:

- 🆔 **ID**
- 🔢 **Version**
- 🕒 **Timestamp**
- 📄 **YAML Preview** (first 100 characters)
- 👁️ **View Button** to load full YAML content 

## 🧑‍💼 12. User Dashboard (Angular Frontend)

A simplified dashboard tailored for **non-admin users**.

### ✅ Features:

- ✅ **Upload YAML** to preview data present in the target PostgreSQL table.
- 🔐 **Authenticated** via JWT token using the `user` role.
- 📄 **Reuses** the same `/data-view` backend logic used by the admin.
- 🧪 Helps users verify table contents before running the ELT job.

> Ideal for analysts or data consumers who need visibility but not full ELT control.

### 📈 Test Coverage Report

- A backend route `/coverage-report` serves the parsed JSON coverage summary.
- The **Admin Dashboard** displays:
  - ✅ **Overall test coverage percentage** (e.g., 87.5%)
  - 📊 **Visual progress bar** to represent coverage graphically
- The coverage report includes:
  - 📄 Total covered lines
  - 📄 Total statements
  - 📊 Percentage of code covered by tests
- ✅ Helps developers ensure that **critical backend logic** is well tested and maintained.

---


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



