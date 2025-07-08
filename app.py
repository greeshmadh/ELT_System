from flask import Flask, jsonify, request
import os
import json

app = Flask(__name__)

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

@app.route('/')
def health():
    return jsonify({"status": "API is running"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
