#!/usr/bin/env python3
"""
Test script to verify Pinecone integration is working
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment variables"""
    print("🔧 Testing environment variables...")
    load_dotenv()
    
    required_vars = [
        "PINECONE_API_KEY",
        "PINECONE_INDEX_NAME", 
        "PINECONE_ENVIRONMENT",
        "PINECONE_CLOUD",
        "GOOGLE_API_KEY"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
        else:
            print(f"✓ {var} is set")
    
    if missing:
        print(f"✗ Missing variables: {', '.join(missing)}")
        return False
    
    return True

def test_imports():
    """Test critical imports"""
    print("\n📦 Testing imports...")
    
    imports_to_test = [
        ("Pinecone", "import pinecone"),
        ("LangChain Pinecone", "from langchain_pinecone import PineconeVectorStore"),
        ("HuggingFace Embeddings", "from langchain_huggingface import HuggingFaceEmbeddings"),
        ("Document", "from langchain_core.documents import Document"),
        ("Text Splitters", "from langchain_text_splitters import RecursiveCharacterTextSplitter"),
        ("Google GenAI", "from langchain_google_genai import ChatGoogleGenerativeAI"),
        ("FastAPI", "import fastapi"),
        ("Uvicorn", "import uvicorn")
    ]
    
    failed_imports = []
    for name, import_statement in imports_to_test:
        try:
            exec(import_statement)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name}: {e}")
            failed_imports.append(name)
    
    return len(failed_imports) == 0

def test_pinecone_connection():
    """Test Pinecone connection"""
    print("\n🌲 Testing Pinecone connection...")
    
    try:
        import pinecone
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        indexes = pc.list_indexes()
        print(f"✓ Connected to Pinecone")
        print(f"  Available indexes: {indexes.names()}")
        
        index_name = os.getenv("PINECONE_INDEX_NAME")
        if index_name in indexes.names():
            print(f"✓ Index '{index_name}' exists")
        else:
            print(f"ℹ️  Index '{index_name}' will be created when needed")
        
        return True
        
    except Exception as e:
        print(f"✗ Pinecone connection failed: {e}")
        return False

def test_knowledge_base_service():
    """Test KnowledgeBaseService initialization"""
    print("\n🧠 Testing KnowledgeBaseService...")
    
    try:
        # Add the current directory to Python path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from services.knowledge_base import KnowledgeBaseService
        
        # Try to initialize the service
        kb_service = KnowledgeBaseService()
        print("✓ KnowledgeBaseService initialized successfully")
        
        # Test if vector store is available
        if kb_service.vector_store is not None:
            print("✓ Vector store is available")
        else:
            print("⚠️  Vector store is None (fallback mode)")
        
        return True
        
    except Exception as e:
        print(f"✗ KnowledgeBaseService failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Pinecone Integration Setup")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Package Imports", test_imports),
        ("Pinecone Connection", test_pinecone_connection),
        ("Knowledge Base Service", test_knowledge_base_service)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Pinecone integration is ready.")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Test API: curl -X POST http://localhost:8000/math/solve -H 'Content-Type: application/json' -d '{\"query\":\"solve x^2-5x+6=0\"}'")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        if passed < 2:
            print("Suggestion: Run 'python fix_dependencies.py' or 'python install_dependencies.py'")

if __name__ == "__main__":
    main()