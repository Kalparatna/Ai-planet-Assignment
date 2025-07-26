#!/usr/bin/env python3
"""
Quick fix for dependency conflicts
This script upgrades conflicting packages to compatible versions
"""

import subprocess
import sys

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return False

def fix_langchain_versions():
    """Fix langchain version conflicts"""
    print("🔧 Fixing LangChain version conflicts...")
    
    # Upgrade to compatible versions
    packages_to_upgrade = [
        "langchain==0.3.72",
        "langchain-community==0.3.0", 
        "langchain-anthropic==0.3.0",
        "langchain-google-genai==2.0.0",
        "langchain-text-splitters==0.3.0"
    ]
    
    for package in packages_to_upgrade:
        if not run_command(f"pip install --upgrade {package}"):
            print(f"Warning: Failed to upgrade {package}")
    
    return True

def fix_tiktoken_conflict():
    """Fix tiktoken version conflict with tavily-python"""
    print("🔧 Fixing tiktoken conflict...")
    
    # Install compatible tiktoken version
    if not run_command("pip install tiktoken==0.5.2"):
        print("Warning: Failed to downgrade tiktoken")
    
    return True

def test_imports():
    """Test if key imports work"""
    print("🧪 Testing imports...")
    
    test_imports = [
        ("Pinecone", "import pinecone"),
        ("LangChain Pinecone", "from langchain_pinecone import PineconeVectorStore"),
        ("HuggingFace Embeddings", "from langchain_huggingface import HuggingFaceEmbeddings"),
        ("Document", "from langchain_core.documents import Document"),
        ("Text Splitters", "from langchain_text_splitters import RecursiveCharacterTextSplitter"),
        ("Google GenAI", "from langchain_google_genai import ChatGoogleGenerativeAI")
    ]
    
    success_count = 0
    for name, import_statement in test_imports:
        try:
            exec(import_statement)
            print(f"✓ {name}")
            success_count += 1
        except ImportError as e:
            print(f"✗ {name}: {e}")
    
    print(f"\n📊 {success_count}/{len(test_imports)} imports successful")
    return success_count == len(test_imports)

def main():
    """Main fix function"""
    print("🛠️  Fixing Dependency Conflicts")
    print("=" * 40)
    
    # Fix version conflicts
    fix_langchain_versions()
    fix_tiktoken_conflict()
    
    # Test if everything works
    if test_imports():
        print("\n✅ All dependencies are working correctly!")
        print("\nYou can now run:")
        print("  python setup_pinecone.py")
        print("  python main.py")
    else:
        print("\n⚠️  Some imports are still failing.")
        print("You may need to run the full installation:")
        print("  python install_dependencies.py")

if __name__ == "__main__":
    main()