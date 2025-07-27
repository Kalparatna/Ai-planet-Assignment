#!/usr/bin/env python3
"""
Fix script to resolve system issues
"""

import subprocess
import sys
import os

def install_missing_packages():
    """Install missing packages"""
    print("📦 Installing missing packages...")
    
    packages = [
        "sentence-transformers==2.2.2",
        "langchain-huggingface==0.1.0"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")

def test_guardrails():
    """Test the updated guardrails"""
    print("\n🛡️ Testing Guardrails...")
    
    try:
        from middleware.guardrails import input_guardrail
        
        test_queries = [
            "What is Area of Triangle?",
            "Find the derivative of x^2",
            "Calculate 2 + 2",
            "Solve quadratic equation",
            "What is the volume of a sphere?",
            "How to find the circumference of a circle?"
        ]
        
        for query in test_queries:
            try:
                result = input_guardrail(query)
                print(f"✅ '{query}' -> Allowed")
            except ValueError as e:
                print(f"❌ '{query}' -> Blocked: {e}")
                
    except Exception as e:
        print(f"❌ Error testing guardrails: {e}")

def test_embeddings():
    """Test embeddings initialization"""
    print("\n🔗 Testing Embeddings...")
    
    try:
        # Test HuggingFace embeddings
        from langchain_huggingface import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        print("✅ HuggingFace embeddings working")
        
        # Test embedding a sample text
        test_text = "What is the area of a triangle?"
        embedding = embeddings.embed_query(test_text)
        print(f"✅ Embedding dimension: {len(embedding)}")
        
    except Exception as e:
        print(f"❌ Embeddings test failed: {e}")

def test_pdf_processor():
    """Test PDF processor initialization"""
    print("\n📄 Testing PDF Processor...")
    
    try:
        from services.pdf_processor import PDFProcessor
        processor = PDFProcessor()
        print("✅ PDF processor initialized")
        
        if processor.embeddings:
            print("✅ PDF embeddings available")
        else:
            print("⚠️  PDF embeddings not available")
            
        if processor.pdf_vector_store:
            print("✅ PDF vector store available")
        else:
            print("⚠️  PDF vector store not available")
            
    except Exception as e:
        print(f"❌ PDF processor test failed: {e}")

def test_knowledge_base():
    """Test knowledge base initialization"""
    print("\n🧠 Testing Knowledge Base...")
    
    try:
        from services.knowledge_base import KnowledgeBaseService
        kb = KnowledgeBaseService()
        print("✅ Knowledge base initialized")
        
        if kb.vector_store:
            print("✅ Vector store available")
        else:
            print("⚠️  Vector store not available (using fallback)")
            
    except Exception as e:
        print(f"❌ Knowledge base test failed: {e}")

def create_sample_data():
    """Create sample data if missing"""
    print("\n📊 Creating Sample Data...")
    
    sample_data_path = "data/sample_data.json"
    
    if not os.path.exists(sample_data_path):
        import json
        os.makedirs("data", exist_ok=True)
        
        sample_data = [
            {
                "id": "geometry-triangle-area",
                "problem": "What is the area of a triangle?",
                "solution": "The area of a triangle can be calculated using the formula: Area = (1/2) × base × height\n\nStep 1: Identify the base and height\nThe base is any side of the triangle, and the height is the perpendicular distance from that base to the opposite vertex.\n\nStep 2: Apply the formula\nArea = (1/2) × base × height\n\nExample: If a triangle has a base of 6 units and height of 4 units:\nArea = (1/2) × 6 × 4 = 12 square units",
                "topic": "Geometry",
                "subtopic": "Triangle Area",
                "difficulty": "Easy",
                "source": "textbook",
                "confidence": 0.95
            },
            {
                "id": "algebra-quadratic",
                "problem": "How to solve quadratic equations?",
                "solution": "Quadratic equations can be solved using several methods:\n\n1. Factoring Method\n2. Quadratic Formula\n3. Completing the Square\n\nQuadratic Formula: x = (-b ± √(b² - 4ac)) / 2a\nFor equation ax² + bx + c = 0",
                "topic": "Algebra",
                "subtopic": "Quadratic Equations",
                "difficulty": "Medium",
                "source": "textbook",
                "confidence": 0.92
            }
        ]
        
        with open(sample_data_path, 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        print(f"✅ Created sample data: {sample_data_path}")
    else:
        print(f"✅ Sample data already exists: {sample_data_path}")

def main():
    """Main fix function"""
    print("🔧 Fixing System Issues")
    print("=" * 50)
    
    # Install missing packages
    install_missing_packages()
    
    # Create sample data
    create_sample_data()
    
    # Test components
    test_guardrails()
    test_embeddings()
    test_pdf_processor()
    test_knowledge_base()
    
    print("\n" + "=" * 50)
    print("✅ System fixes completed!")
    print("\n💡 Next Steps:")
    print("1. Restart your server: python main.py")
    print("2. Test with query: 'What is Area of Triangle?'")
    print("3. Upload a PDF and test PDF functionality")
    print("4. Check that all components are working")

if __name__ == "__main__":
    main()