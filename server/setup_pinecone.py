#!/usr/bin/env python3
"""
Setup script for Pinecone vector database integration
This script helps migrate from Chroma to Pinecone and sets up the initial data
"""

import os
import sys
import json
from dotenv import load_dotenv

def check_requirements():
    """Check if required packages are installed"""
    try:
        import pinecone
        from langchain_pinecone import PineconeVectorStore
        from langchain_huggingface import HuggingFaceEmbeddings
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please install required packages:")
        print("pip install pinecone-client langchain-pinecone")
        return False

def check_env_variables():
    """Check if required environment variables are set"""
    load_dotenv()
    
    required_vars = [
        "PINECONE_API_KEY",
        "PINECONE_INDEX_NAME",
        "PINECONE_ENVIRONMENT",
        "PINECONE_CLOUD"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        return False
    
    print("✓ All required environment variables are set")
    return True

def test_pinecone_connection():
    """Test connection to Pinecone"""
    try:
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        indexes = pc.list_indexes()
        print(f"✓ Successfully connected to Pinecone")
        print(f"  Available indexes: {indexes.names()}")
        return True
    except Exception as e:
        print(f"✗ Failed to connect to Pinecone: {e}")
        return False

def create_sample_data():
    """Create sample data file if it doesn't exist"""
    sample_data_path = "data/sample_data.json"
    
    if os.path.exists(sample_data_path):
        print(f"✓ Sample data file already exists: {sample_data_path}")
        return True
    
    os.makedirs("data", exist_ok=True)
    
    sample_data = [
        {
            "id": "algebra-1",
            "problem": "Solve the quadratic equation: x^2 - 5x + 6 = 0",
            "solution": "To solve x^2 - 5x + 6 = 0, we can factor it as (x-2)(x-3) = 0, giving us x = 2 or x = 3",
            "topic": "Algebra",
            "subtopic": "Quadratic Equations",
            "difficulty": "Medium",
            "source": "textbook",
            "confidence": 0.95
        },
        {
            "id": "calculus-1",
            "problem": "Find the derivative of f(x) = x^3 - 4x^2 + 7x - 9",
            "solution": "Using the power rule: f'(x) = 3x^2 - 8x + 7",
            "topic": "Calculus",
            "subtopic": "Derivatives",
            "difficulty": "Easy",
            "source": "textbook",
            "confidence": 0.98
        },
        {
            "id": "geometry-1",
            "problem": "Find the area of a circle with radius 5 cm",
            "solution": "Area = πr² = π(5)² = 25π ≈ 78.54 cm²",
            "topic": "Geometry",
            "subtopic": "Circle Area",
            "difficulty": "Easy",
            "source": "textbook",
            "confidence": 0.99
        },
        {
            "id": "trigonometry-1",
            "problem": "Prove the identity: sin²θ + cos²θ = 1",
            "solution": "This follows from the Pythagorean theorem in a unit circle where sin θ and cos θ represent the y and x coordinates respectively",
            "topic": "Trigonometry",
            "subtopic": "Identities",
            "difficulty": "Medium",
            "source": "textbook",
            "confidence": 0.92
        },
        {
            "id": "statistics-1",
            "problem": "Calculate the mean of: 4, 7, 2, 8, 4, 9, 4, 6, 3",
            "solution": "Mean = (4+7+2+8+4+9+4+6+3)/9 = 47/9 ≈ 5.22",
            "topic": "Statistics",
            "subtopic": "Descriptive Statistics",
            "difficulty": "Easy",
            "source": "textbook",
            "confidence": 0.99
        }
    ]
    
    try:
        with open(sample_data_path, 'w') as f:
            json.dump(sample_data, f, indent=2)
        print(f"✓ Created sample data file: {sample_data_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to create sample data file: {e}")
        return False

def setup_pinecone_index():
    """Create Pinecone index if it doesn't exist"""
    try:
        from pinecone import Pinecone, ServerlessSpec
        
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = os.getenv("PINECONE_INDEX_NAME")
        
        if index_name in pc.list_indexes().names():
            print(f"✓ Pinecone index '{index_name}' already exists")
            return True
        
        print(f"Creating Pinecone index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=384,  # Dimension for sentence-transformers/all-MiniLM-L6-v2
            metric="cosine",
            spec=ServerlessSpec(
                cloud=os.getenv("PINECONE_CLOUD", "aws"),
                region=os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
            )
        )
        print(f"✓ Created Pinecone index: {index_name}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to create Pinecone index: {e}")
        return False

def load_data_to_pinecone():
    """Load sample data to Pinecone"""
    try:
        print("Loading data to Pinecone...")
        os.system("python load_sample_data.py")
        print("✓ Data loaded to Pinecone successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to load data to Pinecone: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Pinecone for Math Routing Agent")
    print("=" * 50)
    
    steps = [
        ("Checking required packages", check_requirements),
        ("Checking environment variables", check_env_variables),
        ("Testing Pinecone connection", test_pinecone_connection),
        ("Creating sample data", create_sample_data),
        ("Setting up Pinecone index", setup_pinecone_index),
        ("Loading data to Pinecone", load_data_to_pinecone)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Pinecone setup completed successfully!")
    print("\nNext steps:")
    print("1. Start your server: python main.py")
    print("2. Test the API endpoints")
    print("3. Your knowledge base is now using Pinecone embeddings!")

if __name__ == "__main__":
    main()