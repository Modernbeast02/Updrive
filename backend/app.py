import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from rag_tech import RAGProcessor

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'static/UploadedPdfs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

rag = None

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def initialize_rag(file_path):
    global rag
    if rag is None:
        rag = RAGProcessor(pdf_path=file_path, vector_db_collection_name="my_vector_collection", 
                           groq_api_key="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")
        rag.process_pdf_and_store()
        print("RAGProcessor initialized.")

@app.route('/upload', methods=['POST'])
def upload_file():
    print("hi")
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    if file:
        # Save the file to the upload folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Initialize the RAGProcessor only if it's not already initialized
        initialize_rag(file_path)
        
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200
    else:
        return jsonify({'error': 'Failed to upload file'}), 400

@app.route('/query', methods=['GET'])
def get_query():
    global rag
    input_string = request.args.get('input_string')
    print(input_string)

    if not input_string:
        return jsonify({'error': 'No input string provided'}), 400

    if rag is None:
        return jsonify({'error': 'No RAGProcessor instance available'}), 400

    # Process the query
    processed_string, citations = rag.handle_query(input_string)

    return jsonify({'message': 'String processed successfully', 'result': processed_string}), 200

if __name__ == '__main__':
    app.run(debug=True)
