import fitz
import spacy
from sentence_transformers import SentenceTransformer, util
import chromadb
import uuid
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from groq import Groq

os.environ["TOKENIZERS_PARALLELISM"] = "false"

class RAGProcessor:
    def __init__(self, pdf_path, vector_db_collection_name, groq_api_key):
        self.pdf_path = pdf_path
        self.vector_db_collection_name = vector_db_collection_name
        self.nlp = spacy.load("en_core_web_sm")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.Client()
        self.groq_client = Groq(api_key=groq_api_key)
        self.collection = self.client.create_collection(vector_db_collection_name)

    def read_pdf(self):

        pdf_document = fitz.open(self.pdf_path)
        text = ""
        tables = []
        images = []
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text += page.get_text("text")
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if any(char.isdigit() for char in span["text"]):
                                tables.append(span["text"])
            images += page.get_images(full=True)
        pdf_document.close()
        return text, tables, images

    def chunk_sentences_with_clustering_and_similarity(self, sentences, min_word_count=100, max_word_count=300, similarity_threshold=0.7):
        """Cluster sentences and form chunks based on sentence similarity."""
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
        pdf_text, tables, images = self.read_pdf()
        doc = self.nlp(pdf_text)
        sentences = [sent.text for sent in doc.sents]

        semantic_chunks = self.chunk_sentences_with_clustering_and_similarity(sentences)
        embeddings = self.embedding_model.encode(semantic_chunks)

        for chunk, embedding in zip(semantic_chunks, embeddings):
            unique_id = str(uuid.uuid4())
            self.collection.add(
                documents=[chunk],
                embeddings=[embedding.tolist()],
                ids=[unique_id]
            )

    def hybrid_similarity_search(self, query, n_results=8):
        query_embedding = self.embedding_model.encode([query])
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )
        hybrid_results = [result for result in results['documents']]
        return hybrid_results

    def get_bot_response(self, user_input, context):
        detailed_prompt = (
            f"Client query: '{user_input}'\n\n"
            f"Relevant context from the document:\n{context}\n\n"
            f"If it is a deep complex question, break down the query into logical parts, analyze each aspect based on the provided context, "
            f"and provide a detailed answer. Be sure to reason through the steps for a more analytical response, and in the end, "
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
        search_results = self.hybrid_similarity_search(query)
        context = search_results
        bot_response = self.get_bot_response(query, context)
        return bot_response

if __name__ == "__main__":
    pdf_processor = RAGProcessor(pdf_path="amazon.pdf", vector_db_collection_name="my_vector_collection", groq_api_key="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")
    pdf_processor.process_pdf_and_store()
    print("PDF Processed...")
    query = "who is the ceo of amazon"
    response = pdf_processor.handle_query(query)
    print(response)