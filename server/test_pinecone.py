import os
import json
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Test Pinecone connection
def test_pinecone_connection():
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # List indexes
        indexes = pc.list_indexes()
        print(f"Available indexes: {indexes.names()}")
        
        # Test index creation/connection
        index_name = os.getenv("PINECONE_INDEX_NAME", "math-routing-agent")
        
        if index_name in indexes.names():
            print(f"Index '{index_name}' already exists")
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            print(f"Index stats: {stats}")
        else:
            print(f"Index '{index_name}' does not exist")
        
        print("Pinecone connection successful!")
        return True
        
    except Exception as e:
        print(f"Error connecting to Pinecone: {e}")
        return False

# Create sample data file if it doesn't exist
def create_sample_data():
    sample_data_path = "data/sample_data.json"
    
    if not os.path.exists(sample_data_path):
        os.makedirs("data", exist_ok=True)
        
        sample_data = [
            {
                "id": "algebra-1",
                "problem": "Solve the quadratic equation: x^2 - 5x + 6 = 0",
                "solution": "To solve x^2 - 5x + 6 = 0, we factor: (x-2)(x-3) = 0, so x = 2 or x = 3",
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
            }
        ]
        
        with open(sample_data_path, 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        print(f"Created sample data file: {sample_data_path}")
    else:
        print(f"Sample data file already exists: {sample_data_path}")

if __name__ == "__main__":
    print("Testing Pinecone setup...")
    
    # Create sample data
    create_sample_data()
    
    # Test connection
    if test_pinecone_connection():
        print("\nPinecone setup is working correctly!")
    else:
        print("\nPinecone setup failed. Please check your configuration.")