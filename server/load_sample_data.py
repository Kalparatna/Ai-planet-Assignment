import os
import json
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeEmbeddings
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

# Pinecone configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "math-routing-agent")
ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
CLOUD = os.getenv("PINECONE_CLOUD", "aws")

# Initialize Pinecone
print("Initializing Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Load sample data
print("Loading sample data...")
with open('data/sample_data.json', 'r') as f:
    sample_data = json.load(f)

# Check if Pinecone index exists, create if not
if INDEX_NAME not in pc.list_indexes().names():
    print(f"Creating Pinecone index: {INDEX_NAME}")
    # Get the correct dimension for the Pinecone embedding model
    embedding_model_name = os.getenv("PINECONE_EMBEDDING_MODEL", "llama-text-embed-v2")
    model_dimensions = {
        "multilingual-e5-large": 1024,
        "text-embedding-ada-002": 1536,
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "llama-text-embed-v2": 4096,
        "text-embedding-gecko": 768,
        "text-embedding-gecko-multilingual": 768
    }
    dimension = model_dimensions.get(embedding_model_name, 1536)
    
    pc.create_index(
        name=INDEX_NAME,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(
            cloud=CLOUD,
            region=ENVIRONMENT
        )
    )
    print(f"Created Pinecone index: {INDEX_NAME}")

# Get the index
index = pc.Index(INDEX_NAME)

# Initialize Pinecone embedding model
print("Initializing Pinecone embedding model...")
embedding_model = PineconeEmbeddings(
    api_key=PINECONE_API_KEY,
    model=os.getenv("PINECONE_EMBEDDING_MODEL", "llama-text-embed-v2")
)

# Initialize PineconeVectorStore
vector_store = PineconeVectorStore(
    index=index,
    embedding=embedding_model,
    text_key="text"
)

# Prepare documents for vector store
print("Preparing documents for vector store...")
documents = []

for item in sample_data:
    # Create document text (problem + solution)
    content = f"Problem: {item['problem']}\nSolution: {item['solution']}"
    
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
    
    documents.append(Document(page_content=content, metadata=metadata))

# Add documents to Pinecone
print("Adding documents to Pinecone vector store...")
vector_store.add_documents(documents)

print(f"Successfully loaded {len(sample_data)} sample problems into the Pinecone knowledge base.")
print(f"Vector store saved to Pinecone index: {INDEX_NAME}")