from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Table, MetaData,text
import yaml
import os
import json
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta
from flask_cors import CORS
import subprocess
import uuid
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError



app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config["JWT_SECRET_KEY"] = "your-secret-key" 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

UPLOAD_FOLDER = './uploaded_configs/'
ALLOWED_EXTENSIONS = {'yaml', 'yml'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/data', methods=['GET'])
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_api_data():
    folder_path = request.args.get('path', './data/api')  # Default fallback
    combined_data = []

    if not os.path.exists(folder_path):
        return jsonify({"error": "API data folder not found"}), 500

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            full_path = os.path.join(folder_path, filename)
            try:
                with open(full_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        combined_data.extend(data)
                    else:
                        combined_data.append(data)
            except Exception as e:
                return jsonify({"error": f"Failed to read {filename}: {str(e)}"}), 500

    return jsonify(combined_data), 200


@app.route('/config-history', methods=['GET'])
@jwt_required()
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_config_history():
    try:
        engine = create_engine('postgresql://elt_user:elt_password@localhost:5432/elt_db')
        metadata = MetaData()
        config_history = Table('config_history', metadata, autoload_with=engine)

        with engine.connect() as conn:
            result = conn.execute(config_history.select().order_by(config_history.c.version.desc()))
            history = [{
                "id": row.id,
                "version": row.version,
                "timestamp": row.timestamp.strftime("%Y-%m-%d %H:%M"),
                "yaml_preview": row.yaml_content[:100]
            } for row in result]

        return jsonify({"configs": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/config/<int:config_id>', methods=['GET'])
@jwt_required()
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_single_config(config_id):
    try:
        engine = create_engine('postgresql://elt_user:elt_password@localhost:5432/elt_db')
        metadata = MetaData()
        config_history = Table('config_history', metadata, autoload_with=engine)

        with engine.connect() as conn:
            result = conn.execute(config_history.select().where(config_history.c.id == config_id)).fetchone()
            if result:
                return jsonify({
                    "id": result.id,
                    "version": result.version,
                    "timestamp": result.timestamp.strftime("%Y-%m-%d %H:%M"),
                    "yaml_content": result.yaml_content
                })
            else:
                return jsonify({"error": "Config not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/logs', methods=['GET'])
@jwt_required()
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_logs():
    try:
        with open("elt.log", "r") as f:
            lines = f.readlines()[-100:]  # returns last 100 lines
        return jsonify({"logs": lines})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/')
def health():
    return jsonify({"status": "API is running"}), 200

# Mock users
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"}
}

@app.route('/auth/login', methods=['POST'])
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=username)
    return jsonify({"token": token, "role": user["role"]})

@app.route('/data-view', methods=['POST'])
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def data_view_from_uploaded_yaml():
    if request.method == 'OPTIONS':
        return '', 200

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            # Save the uploaded YAML
            unique_name = f"{uuid.uuid4().hex}_{file.filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_name)
            file.save(file_path)

            # Read YAML to get DB and table info
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)

            db_name = config.get('target', {}).get('database')
            table_name = config.get('target', {}).get('table')

            if not db_name or not table_name:
                return jsonify({"error": "'database' or 'table' not found under 'target' in YAML"}), 400

            # Create dynamic engine based on YAML DB name
            engine = create_engine(f'postgresql://elt_user:elt_password@localhost:5432/{db_name}')

            with engine.connect() as conn:
                query = text(f"SELECT * FROM {table_name} LIMIT 100")
                result = conn.execute(query)
                columns = list(result.keys())
                rows = [dict(zip(columns, row)) for row in result]

            return jsonify({"columns": columns, "rows": rows})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid file format"}), 400


@app.route('/trigger-job', methods=['POST'])
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def trigger_job():
    if request.method == 'OPTIONS':
        return '', 200
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        unique_name = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(file_path)

        try:
            subprocess.Popen(['python', 'scheduleAndManual.py', file_path])
            return jsonify({"message": "ELT job triggered successfully!"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format"}), 400

@app.route('/coverage-report', methods=['GET'])
@jwt_required()
def get_coverage_report():
    try:
        with open("coverage.json", "r") as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
