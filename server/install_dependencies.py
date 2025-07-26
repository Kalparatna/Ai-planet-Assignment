#!/usr/bin/env python3
"""
Clean installation script for Pinecone integration dependencies
This script resolves version conflicts and installs compatible packages
"""

import subprocess
import sys
import os

def run_command(command, ignore_errors=False):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {command}")
        return True
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            print(f"⚠️ {command} (ignored)")
            return True
        else:
            print(f"✗ {command}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False

def uninstall_conflicting_packages():
    """Uninstall packages that might cause conflicts"""
    conflicting_packages = [
        "langchain",
        "langchain-community", 
        "langchain-core",
        "langchain-openai",
        "langchain-anthropic",
        "langchain-google-genai",
        "langchain-text-splitters",
        "langsmith",
        "tiktoken"
    ]
    
    print("🧹 Cleaning up conflicting packages...")
    for package in conflicting_packages:
        run_command(f"pip uninstall -y {package}", ignore_errors=True)
    
    return True  # Always return True since we ignore errors

def install_core_packages():
    """Install core packages first"""
    core_packages = [
        "fastapi==0.110.0",
        "uvicorn==0.29.0", 
        "python-dotenv==1.0.1",
        "python-multipart==0.0.9",
        "requests==2.32.4",
        "numpy",
        "sentence-transformers==2.2.2"
    ]
    
    print("\n📦 Installing core packages...")
    for package in core_packages:
        if not run_command(f"pip install {package}"):
            return False
    return True

def install_langchain_packages():
    """Install langchain packages with compatible versions"""
    langchain_packages = [
        "langchain-core==0.3.72",
        "langsmith==0.4.8", 
        "langchain-text-splitters==0.3.0",
        "langchain-community==0.3.0",
        "langchain==0.3.0",
        "langchain-openai==0.3.28",
        "langchain-google-genai==2.0.0"
    ]
    
    print("\n🔗 Installing LangChain packages...")
    for package in langchain_packages:
        if not run_command(f"pip install {package}"):
            return False
    return True

def install_pinecone_packages():
    """Install Pinecone packages"""
    pinecone_packages = [
        "pinecone-client==5.0.0",
        "langchain-pinecone==0.2.11"
    ]
    
    print("\n🌲 Installing Pinecone packages...")
    for package in pinecone_packages:
        if not run_command(f"pip install {package}"):
            return False
    return True

def install_remaining_packages():
    """Install remaining application packages"""
    remaining_packages = [
        "tavily-python==0.3.1",
        "dspy==2.5.15",
        "bs4==0.0.2",
        "beautifulsoup4==4.12.3",
        "fastapi-cors==0.0.6",
        "pyarrow==14.0.1",
        "typer==0.9.0",
        "pytz==2024.1",
        "tenacity==8.2.3"
    ]
    
    print("\n📚 Installing remaining packages...")
    for package in remaining_packages:
        if not run_command(f"pip install {package}"):
            print(f"Warning: Failed to install {package}, continuing...")
    return True

def verify_installation():
    """Verify that key packages are installed correctly"""
    test_imports = [
        "import pinecone",
        "from langchain_pinecone import PineconeVectorStore", 
        "from langchain_huggingface import HuggingFaceEmbeddings",
        "from langchain_core.documents import Document",
        "from langchain_text_splitters import RecursiveCharacterTextSplitter",
        "import fastapi",
        "import uvicorn"
    ]
    
    print("\n🔍 Verifying installation...")
    for test_import in test_imports:
        try:
            exec(test_import)
            print(f"✓ {test_import}")
        except ImportError as e:
            print(f"✗ {test_import} - {e}")
            return False
    
    return True

def main():
    """Main installation function"""
    print("🚀 Installing Pinecone Integration Dependencies")
    print("=" * 60)
    
    steps = [
        ("Uninstalling conflicting packages", uninstall_conflicting_packages),
        ("Installing core packages", install_core_packages),
        ("Installing LangChain packages", install_langchain_packages), 
        ("Installing Pinecone packages", install_pinecone_packages),
        ("Installing remaining packages", install_remaining_packages),
        ("Verifying installation", verify_installation)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"\n❌ Installation failed at: {step_name}")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Installation completed successfully!")
    print("\nNext steps:")
    print("1. Run: python setup_pinecone.py")
    print("2. Start your server: python main.py")

if __name__ == "__main__":
    main()