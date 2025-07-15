from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Table, MetaData
import yaml
import os
import json
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta
from flask_cors import CORS


app = Flask(__name__)

CORS(app)
app.config["JWT_SECRET_KEY"] = "your-secret-key"  # use env var in production
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)


@app.route('/api/data', methods=['GET'])
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
                "yaml_preview": row.yaml_content[:100]  # just first 100 chars
            } for row in result]

        return jsonify({"configs": history})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open("elt.log", "r") as f:
            lines = f.readlines()[-100:]  # return last 100 lines
        return jsonify({"logs": lines})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/data-view', methods=['GET'])
@jwt_required()
def get_data_view():
    user = get_jwt_identity()
    if user["role"] != "admin":
        return jsonify({"error": "Access denied"}), 403

    try:
        engine = create_engine('postgresql://elt_user:elt_password@localhost:5432/elt_db')
        table_name = "raw_data"

        with engine.connect() as conn:
            result = conn.execute(f"SELECT * FROM {table_name} ORDER BY 1 DESC LIMIT 100")
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result]

        return jsonify({"columns": columns, "rows": rows})

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
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity={"username": username, "role": user["role"]})
    return jsonify({"token": token, "role": user["role"]})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
