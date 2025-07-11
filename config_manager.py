import os
import yaml
import datetime
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Table, Column, Integer, Text, MetaData, DateTime
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = './uploaded_configs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database setup
engine = create_engine('postgresql://elt_user:elt_password@localhost:5432/elt_db')
metadata = MetaData()#MetaData is a container object that holds information about tables.

# Config history table
config_history = Table('config_history', metadata,
    Column('id', Integer, primary_key=True),
    Column('version', Integer),
    Column('timestamp', DateTime),
    Column('yaml_content', Text)
)
metadata.create_all(engine)#This creates the table in the elt_db PostgreSQL database if it doesn't already exist.

@app.route('/upload-config', methods=['POST'])
def upload_config():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    try:
        with open(path, 'r') as f:
            content = f.read()
            parsed_yaml = yaml.safe_load(content)
    except Exception as e:
        return jsonify({'error': f'Invalid YAML: {e}'}), 400

    try:
        with engine.begin() as conn:
            result = conn.execute(
                config_history.select()
                .order_by(config_history.c.version.desc())
                .limit(1)
            ).fetchone()

            next_version = (result[1] + 1) if result else 1

            conn.execute(config_history.insert().values(
                version=next_version,
                timestamp=datetime.datetime.now(),
                yaml_content=content
            ))

        return jsonify({'message': 'YAML uploaded successfully', 'version': next_version}), 200

    except Exception as e:
        return jsonify({'error': f'Database error: {e}'}), 500

if __name__ == "__main__":
    app.run(port=5055)


# Add at the bottom of config_manager.py
def upload_if_new_config(yaml_path):
    with open(yaml_path, 'r') as f:
        new_content = f.read()
        parsed_yaml = yaml.safe_load(new_content)  # validate syntax

    engine = create_engine('postgresql://elt_user:elt_password@localhost:5432/elt_db')
    metadata = MetaData()
    config_history = Table('config_history', metadata,
        Column('id', Integer, primary_key=True),
        Column('version', Integer),
        Column('timestamp', DateTime),
        Column('yaml_content', Text)
    )
    metadata.create_all(engine)

    with engine.begin() as conn:
        existing_versions = conn.execute(config_history.select().order_by(config_history.c.version.desc())).fetchall()
        for row in existing_versions:
            if row.yaml_content.strip() == new_content.strip():
                return f"Config already exists as version {row.version}"

        next_version = (existing_versions[0].version + 1) if existing_versions else 1

        conn.execute(config_history.insert().values(
            version=next_version,
            timestamp=datetime.datetime.now(),
            yaml_content=new_content
        ))

    return f"New config stored as version {next_version}"
