import os
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Load sample data
print("Loading sample data...")
with open('data/sample_data.json', 'r') as f:
    sample_data = json.load(f)

# Prepare documents for vector store
print("Preparing documents for vector store...")
documents = []
metadatas = []

for item in sample_data:
    # Create document text (problem + solution)
    document = f"Problem: {item['problem']}\nSolution: {item['solution']}"
    documents.append(document)
    
    # Create metadata
    metadata = {
        'id': item['id'],
        'problem': item['problem'],
        'topic': item['topic'],
        'subtopic': item['subtopic'],
        'difficulty': item['difficulty'],
        'source': item['source'],
        'confidence': item['confidence']
    }
    metadatas.append(metadata)

# Initialize embedding model
print("Initializing embedding model...")
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Create vector store
print("Creating vector store...")
vector_store = Chroma.from_texts(
    texts=documents,
    embedding=embedding_model,
    metadatas=metadatas,
    persist_directory="data/chroma_db"
)

# Persist the vector store
print("Persisting vector store...")
vector_store.persist()

print(f"Successfully loaded {len(sample_data)} sample problems into the knowledge base.")
print("Vector store saved to data/chroma_db")