from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'static/UploadedPdfs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    # Save the file to the uploads directory
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    return 'File uploaded successfully', 200


if __name__ == '__main__':
    app.run(debug=True, port=8080)