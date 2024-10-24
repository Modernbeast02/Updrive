import os
from flask import Flask, jsonify, request, make_response, send_file
from flask_cors import CORS
import json
from rag_tech_new import RAGProcessor

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'static/UploadedPdfs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
curr_file=None
rag = None

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def initialize_rag(file_path):
    global curr_file
    curr_file =file_path
    global rag
    rag = RAGProcessor(pdf_path=file_path,
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

@app.route('/questions', methods=['GET'])
def get_questions():
    global rag
    query = "Generate 5 random Questions about the pdf in input do not generate any answer"
    citations = []
    response,citations,context = rag.handle_query(query)
    n = response.split("\n")
    print(n)
    g = []
    for i in n:
            if(len(i) > 1):
                if(i[0].isdigit() == True):
                    g.append(i)
    print(g)
    return jsonify({"ques":g}),200
@app.route('/query', methods=['GET'])
def get_query():
    global rag
    global curr_file
    input_string = request.args.get('input_string')
    print(input_string)

    if not input_string:
        return jsonify({'error': 'No input string provided'}), 400

    if rag is None:
        return jsonify({'error': 'No RAGProcessor instance available'}), 400

    # Process the query
    processed_string,citations,context = rag.handle_query(input_string)

    
    print(citations)
    for i in sorted(set(citations)):
        if(str(i).isdigit()):
            print(curr_file)
            rag.highlight_and_append_pdf_page(input_pdf=curr_file,output_pdf='output.pdf',page_number=i+1)
    rag.highlight_similar_chunks_in_pdf('output.pdf', input_string, threshold=0.3, chunk_size=100) # in this input the output pdf to get the highlighted pdf

    return jsonify({'message': 'String processed successfully', 'result': processed_string}), 200

@app.route('/citation', methods=['GET'])
def get_citation():
    # Create a response object
    response = make_response(send_file('highlighted.pdf', as_attachment=True))
    
    return response

if __name__ == '__main__':
    app.run(debug=True)
