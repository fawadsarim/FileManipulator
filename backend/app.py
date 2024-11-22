from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS  # Import Flask-CORS
import os
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploaded_files'
PROCESSED_FOLDER = 'processed_files'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    file_extension = file.filename.split('.')[-1]
    if file_extension == 'csv':
        df = pd.read_csv(file_path)
    elif file_extension in ['xls', 'xlsx']:
        df = pd.read_excel(file_path)
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    df.drop(df.columns[1], axis=1, inplace=True)

    processed_file_path = os.path.join(PROCESSED_FOLDER, f'processed_{file.filename}')
    if file_extension == 'csv':
        df.to_csv(processed_file_path, index=False)
    else:
        df.to_excel(processed_file_path, index=False)

    return jsonify({'download_url': f'/download/processed_{file.filename}'}), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
