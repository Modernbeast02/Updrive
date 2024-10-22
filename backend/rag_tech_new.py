import spacy
from sentence_transformers import SentenceTransformer, util
import chromadb
import uuid
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from groq import Groq
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO
from gtts import gTTS
from playsound import playsound
import fitz
import time
from datetime import datetime

os.environ["TOKENIZERS_PARALLELISM"] = "false"

class RAGProcessor:
    def __init__(self, pdf_path, groq_api_key):
        self.pdf_path = pdf_path
        self.nlp = spacy.load("en_core_web_sm")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.HttpClient(host="chroma", port=8000)
        self.groq_client = Groq(api_key=groq_api_key)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        file_name = os.path.basename(pdf_path).split('.')[0]
        self.vector_db_collection_name = f"{file_name}_{timestamp}"
        # self.delete_old_collections()
        self.collection = self.client.create_collection(self.vector_db_collection_name)

    def delete_old_collections(self):
        existing_collections = self.client.list_collections()
        for collection in existing_collections:
            self.client.delete_collection(collection['name'])  

    def read_pdf(self):
        reader = PdfReader(self.pdf_path)
        text = ""
        tables = []
        images = []
        line_info = []

        for page_num, page in enumerate(reader.pages):
            text += page.extract_text()
            for line_number, line in enumerate(text.splitlines(), start=1):
                if any(char.isdigit() for char in line):
                    tables.append(line)
                line_info.append({"page": page_num, "line": line_number, "text": line})
        return text, tables, images, line_info

    def chunk_sentences_with_clustering_and_similarity(self, sentences, min_word_count=100, max_word_count=300, similarity_threshold=0.7):
        embeddings = self.embedding_model.encode(sentences)
        n_clusters = max(1, len(sentences) // (min_word_count // 20))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(embeddings)

        context_chunks = []
        for cluster_label in np.unique(cluster_labels):
            cluster_sentences = [sentences[i] for i in range(len(sentences)) if cluster_labels[i] == cluster_label]
            cluster_embeddings = embeddings[cluster_labels == cluster_label]
            similarity_matrix = cosine_similarity(cluster_embeddings)
            visited = set()

            for i, sentence in enumerate(cluster_sentences):
                if i in visited:
                    continue
                current_chunk = [sentence]
                visited.add(i)
                for j in range(len(cluster_sentences)):
                    if j not in visited and similarity_matrix[i][j] >= similarity_threshold:
                        current_chunk.append(cluster_sentences[j])
                        visited.add(j)

                chunk_text = ' '.join(current_chunk)
                if min_word_count <= len(chunk_text.split()) <= max_word_count:
                    context_chunks.append(chunk_text)

        return context_chunks

    def process_pdf_and_store(self):
        pdf_text, tables, images, line_info = self.read_pdf()
        doc = self.nlp(pdf_text)
        sentences = [sent.text for sent in doc.sents]

        semantic_chunks = self.chunk_sentences_with_clustering_and_similarity(sentences)
        embeddings = self.embedding_model.encode(semantic_chunks)

        for chunk, embedding in zip(semantic_chunks, embeddings):
            matching_lines = [info for info in line_info if chunk.startswith(info["text"])]
            if matching_lines:
                page_number = matching_lines[0]["page"]
                line_number = matching_lines[0]["line"]
            else:
                page_number = 0
                line_number = 1

            unique_id = str(uuid.uuid4())
            metadata = {
                "page_number": page_number,
                "line_number": line_number,
                "chunk_id": unique_id
            }

            self.collection.add(
                documents=[chunk],
                embeddings=[embedding.tolist()],
                ids=[unique_id],
                metadatas=[metadata]
            )

    def hybrid_similarity_search(self, query, n_results=8):
        query_embedding = self.embedding_model.encode([query])
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )
        c = results["metadatas"][0]
        citation = []
        for i in c:
            page_number = i['page_number']
            citation.append(page_number)
        hybrid_results = [result for result in results['documents']]
        return hybrid_results, citation

    def get_bot_response(self, user_input, context):
        detailed_prompt = (
            f"Client query: '{user_input}'\n\n"

            "Using the relevant context from the document:"

            f"{context}"
            '''
            Follow these steps to solve the query accurately:

            the question might be numeric , mcq or just a general question deal with it accordingly

            Clarify the question: Break down the user’s input to understand what specific numerical result is being asked for. Identify the values provided in the user input and what kind of result (calculation, comparison, etc.) is expected.

            Extract key values: Identify and list out the relevant numbers, variables, and any other important information from the user input.

            Apply formulas from the context: Use any formulas, examples, or procedures given in the context to solve the problem. Clearly outline how these formulas fit the specific problem based on the input.

            Perform step-by-step calculations: Solve the problem using the formulas and values, executing each calculation carefully. Ensure precision by checking units and applying correct mathematical operations.

            Verify the result: Analyze whether the calculated result aligns logically with the context. Ensure the answer makes sense given the user's input and context-based formulas.

            Provide the final answer: Present the numerical result, along with an explanation of how the values from the input and formulas from the context were used to arrive at the solution. Clearly justify why this answer is correct.

            Be sure to validate each step and ensure the answer is accurate and well-reasoned.

            give the correct answer in the end give a valid reason for the answer
            '''
        )

        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a question-answering chatbot."},
                {"role": "user", "content": detailed_prompt}
            ],
            model="llama3-8b-8192",
            max_tokens=1000
        )
        return chat_completion.choices[0].message.content

    def handle_query(self, query):
        search_results, citations = self.hybrid_similarity_search(query)
        context = search_results
        bot_response = self.get_bot_response(query, context)
        return bot_response, citations, context

    def highlight_and_append_pdf_page(self, input_pdf: str, output_pdf: str, page_number: int):
        reader = PdfReader(input_pdf)
        if page_number < 1 or page_number > len(reader.pages):
            raise ValueError("Invalid page number")
        page = reader.pages[page_number - 1]
        writer = PdfWriter()
        try:
            existing_output_reader = PdfReader(output_pdf)
            for existing_page in range(len(existing_output_reader.pages)):
                writer.add_page(existing_output_reader.pages[existing_page])
        except FileNotFoundError:
            print(f"Creating new output PDF: {output_pdf}")
        writer.add_page(page)
        with open(output_pdf, 'wb') as f:
            writer.write(f)
        print(f"Page {page_number} fully highlighted and saved to {output_pdf}")

    def text_to_audio(self, text, lang='en', filename='output.mp3'):
        try:
            tts = gTTS(text=text, lang=lang)
            tts.save(filename)
            playsound(filename)
            os.remove(filename)
        except Exception as e:
            print(f"An error occurred: {e}")

    def split_text_into_chunks(self, text, chunk_size=100):
        words = text.split()
        return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

    def highlight_similar_chunks_in_pdf(self, pdf_path, query, threshold=0.7, chunk_size=100):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        document = fitz.open(pdf_path)
        highlighted_pages = []


        for page_num in range(len(document)):
            page = document[page_num]
            text = page.get_text("text")
            text_chunks = self.split_text_into_chunks(text, chunk_size)
            query_embedding = model.encode(query, convert_to_tensor=True)

            for chunk in text_chunks:
                if chunk.strip():
                    chunk_embedding = model.encode(chunk, convert_to_tensor=True)
                    similarity = util.pytorch_cos_sim(query_embedding, chunk_embedding).item()

                    if similarity > threshold:
                        text_instances = page.search_for(chunk)
                        for inst in text_instances:
                            highlight = page.add_highlight_annot(inst)

            highlighted_pages.append(page_num)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        highlighted_pdf_path = f"highlighted.pdf"
    
        document.save(highlighted_pdf_path)
        document.close()

        print(f"Highlighted PDF saved as: {highlighted_pdf_path}")
        return highlighted_pdf_path


if __name__ == "__main__":
    ## for highlighting pdf
    '''
    pdf_processor = RAGProcessor(pdf_path="amazon.pdf", groq_api_key="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")
    pdf_processor.process_pdf_and_store()
    query = "who is the ceo of amazon"

    response, citations, context = pdf_processor.handle_query(query)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_pdf = f"output_{timestamp}.pdf"

    print(response)
    print(context)

    for i in sorted(set(citations)):
        if(str(i).isdigit()):
            pdf_processor.highlight_and_append_pdf_page(input_pdf='amazon.pdf', output_pdf=output_pdf, page_number=int(i) + 1)

    pdf_processor.highlight_similar_chunks_in_pdf(output_pdf, query, threshold=0.5, chunk_size=100) # in this input the output pdf to get the highlighted pdf
    '''

    ## for suggesting 5 questions
    pdf_processor = RAGProcessor(pdf_path="amazon.pdf", groq_api_key="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")
    pdf_processor.process_pdf_and_store()
    query = "Generate 5 random Questions Regarding the amazon company do not generate any answer"
    citations = []

    response,citations,context = pdf_processor.handle_query(query)
    n = response.split("\n")
    print(n)
    g = []
    for i in n:
            if(len(i) > 1):
                if(i[0].isdigit() == True):
                    g.append(i)
    print(g)
    