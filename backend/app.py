import os
from flask import Flask, jsonify, request  # Import request from Flask
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

UPLOAD_FOLDER = 'static/UploadedPdfs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    print("hi")
    # Use the request object from Flask to access the uploaded file
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    if file:
        # Save the file to the upload folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200
    else:
        return jsonify({'error': 'Failed to upload file'}), 400

if __name__ == '__main__':
    app.run(debug=True)
