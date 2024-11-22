from flask import Flask, render_template, request, send_from_directory
import os
import pandas as pd

app = Flask(__name__)

# Configure upload and processed folders
UPLOAD_FOLDER = 'uploaded_files'
PROCESSED_FOLDER = 'processed_files'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the file is present in the request
        if 'file' not in request.files:
            return render_template('index.html', error="No file uploaded")

        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No file selected")

        # Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Process the file
        file_extension = file.filename.split('.')[-1]
        if file_extension == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Remove the second column
        df.drop(df.columns[1], axis=1, inplace=True)

        # Save the processed file
        processed_file_path = os.path.join(app.config['PROCESSED_FOLDER'], f'processed_{file.filename}')
        if file_extension == 'csv':
            df.to_csv(processed_file_path, index=False)
        else:
            df.to_excel(processed_file_path, index=False)

        return render_template('index.html', download_url=f'/download/{file.filename}')

    return render_template('index.html')


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    processed_file_path = os.path.join(app.config['PROCESSED_FOLDER'], f'processed_{filename}')
    return send_from_directory(app.config['PROCESSED_FOLDER'], f'processed_{filename}', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
