#!/usr/bin/env python3
"""
Quick installation script for Pinecone integration
This script installs packages without uninstalling first
"""

import subprocess
import sys

def install_package(package):
    """Install a single package"""
    try:
        print(f"Installing {package}...")
        result = subprocess.run(
            f"pip install {package}", 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✓ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Main installation function"""
    print("🚀 Quick Install for Pinecone Integration")
    print("=" * 50)
    
    # Essential packages for Pinecone integration
    packages = [
        "pinecone-client==5.0.0",
        "langchain-pinecone==0.2.11",
        "langchain-core==0.3.72",
        "langchain-text-splitters==0.3.0",
        "langchain-community==0.3.0",
        "langchain==0.3.0",
        "langchain-google-genai==2.0.0",
        "sentence-transformers==2.2.2"
    ]
    
    failed_packages = []
    
    for package in packages:
        if not install_package(package):
            failed_packages.append(package)
    
    print("\n" + "=" * 50)
    
    if not failed_packages:
        print("🎉 All packages installed successfully!")
        
        # Test imports
        print("\n🧪 Testing imports...")
        test_imports = [
            ("Pinecone", "import pinecone"),
            ("LangChain Pinecone", "from langchain_pinecone import PineconeVectorStore"),
            ("HuggingFace Embeddings", "from langchain_huggingface import HuggingFaceEmbeddings"),
            ("Document", "from langchain_core.documents import Document"),
            ("Text Splitters", "from langchain_text_splitters import RecursiveCharacterTextSplitter")
        ]
        
        all_imports_work = True
        for name, import_statement in test_imports:
            try:
                exec(import_statement)
                print(f"✓ {name}")
            except ImportError as e:
                print(f"✗ {name}: {e}")
                all_imports_work = False
        
        if all_imports_work:
            print("\n✅ Ready to use Pinecone!")
            print("\nNext steps:")
            print("1. Run: python setup_pinecone.py")
            print("2. Start your server: python main.py")
        else:
            print("\n⚠️ Some imports failed. You may need to resolve dependency conflicts.")
    else:
        print(f"❌ Failed to install: {', '.join(failed_packages)}")
        print("\nTry running with --upgrade flag:")
        for package in failed_packages:
            print(f"pip install --upgrade {package}")

if __name__ == "__main__":
    main()