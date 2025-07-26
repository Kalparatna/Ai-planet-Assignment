#!/usr/bin/env python3
"""
Debug script to check Pinecone connection issues
"""

import os
from dotenv import load_dotenv

def debug_pinecone():
    """Debug Pinecone connection step by step"""
    
    print("🔍 Debugging Pinecone Connection")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    print("\n1. Checking Environment Variables:")
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    environment = os.getenv("PINECONE_ENVIRONMENT")
    cloud = os.getenv("PINECONE_CLOUD")
    model = os.getenv("PINECONE_EMBEDDING_MODEL")
    
    print(f"   API Key: {'✓ Set' if api_key else '✗ Missing'}")
    print(f"   Index Name: {index_name}")
    print(f"   Environment: {environment}")
    print(f"   Cloud: {cloud}")
    print(f"   Model: {model}")
    
    if not api_key:
        print("\n❌ PINECONE_API_KEY is missing!")
        return False
    
    # Test Pinecone import
    print("\n2. Testing Pinecone Import:")
    try:
        from pinecone import Pinecone
        print("   ✓ Pinecone imported successfully")
    except ImportError as e:
        print(f"   ✗ Failed to import Pinecone: {e}")
        return False
    
    # Test Pinecone connection
    print("\n3. Testing Pinecone Connection:")
    try:
        pc = Pinecone(api_key=api_key)
        print("   ✓ Pinecone client created")
    except Exception as e:
        print(f"   ✗ Failed to create Pinecone client: {e}")
        return False
    
    # Test listing indexes
    print("\n4. Testing Index Listing:")
    try:
        indexes = pc.list_indexes()
        print(f"   ✓ Available indexes: {indexes.names()}")
        
        if index_name in indexes.names():
            print(f"   ✓ Index '{index_name}' exists")
        else:
            print(f"   ⚠️  Index '{index_name}' does not exist (will be created)")
    except Exception as e:
        print(f"   ✗ Failed to list indexes: {e}")
        return False
    
    # Test PineconeEmbeddings import
    print("\n5. Testing PineconeEmbeddings:")
    try:
        from langchain_pinecone import PineconeEmbeddings
        print("   ✓ PineconeEmbeddings imported successfully")
        
        # Try to create embeddings instance
        embeddings = PineconeEmbeddings(
            api_key=api_key,
            model=model
        )
        print("   ✓ PineconeEmbeddings instance created")
        
    except Exception as e:
        print(f"   ✗ Failed to create PineconeEmbeddings: {e}")
        print(f"   💡 This might be why the knowledge base is falling back to in-memory store")
        return False
    
    print("\n✅ All Pinecone tests passed!")
    return True

def debug_tavily():
    """Debug Tavily API connection"""
    
    print("\n🔍 Debugging Tavily Connection")
    print("=" * 50)
    
    # Check Tavily API key
    tavily_key = os.getenv("TAVILY_API_KEY")
    print(f"\nTavily API Key: {'✓ Set' if tavily_key else '✗ Missing'}")
    
    if not tavily_key:
        print("❌ TAVILY_API_KEY is missing!")
        return False
    
    # Test Tavily import and connection
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=tavily_key)
        print("✓ Tavily client created successfully")
        
        # Test a simple search
        result = client.search("test query", max_results=1)
        print("✓ Tavily API is working")
        return True
        
    except Exception as e:
        print(f"✗ Tavily API error: {e}")
        return False

if __name__ == "__main__":
    pinecone_ok = debug_pinecone()
    tavily_ok = debug_tavily()
    
    print("\n" + "=" * 50)
    print("📊 Debug Summary:")
    print(f"   Pinecone: {'✅ Working' if pinecone_ok else '❌ Issues found'}")
    print(f"   Tavily: {'✅ Working' if tavily_ok else '❌ Issues found'}")
    
    if not pinecone_ok:
        print("\n💡 Pinecone Issues - Possible Solutions:")
        print("   1. Check your PINECONE_API_KEY is correct")
        print("   2. Ensure you have the right packages: pip install langchain-pinecone")
        print("   3. Verify your Pinecone account is active")
    
    if not tavily_ok:
        print("\n💡 Tavily Issues - Possible Solutions:")
        print("   1. Check your TAVILY_API_KEY is correct")
        print("   2. Verify your Tavily account is active")
        print("   3. Check if you have API credits remaining")