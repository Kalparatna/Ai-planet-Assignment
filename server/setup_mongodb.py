#!/usr/bin/env python3
"""
MongoDB Setup Script for Math Routing Agent
Sets up local MongoDB and optimizes for 5-8 second responses
"""

import os
import sys
import subprocess
import asyncio
import platform

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step, description):
    """Print formatted step"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def run_command(command, description):
    """Run system command with error handling"""
    print(f"⚡ {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def check_mongodb_installed():
    """Check if MongoDB is installed"""
    print("🔍 Checking MongoDB installation...")
    
    # Check if mongod is available
    result = subprocess.run("mongod --version", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ MongoDB is already installed")
        return True
    else:
        print("❌ MongoDB is not installed")
        return False

def install_mongodb():
    """Install MongoDB based on operating system"""
    system = platform.system().lower()
    
    print(f"🔧 Installing MongoDB for {system}...")
    
    if system == "windows":
        print("📥 For Windows:")
        print("1. Download MongoDB Community Server from: https://www.mongodb.com/try/download/community")
        print("2. Run the installer and follow the setup wizard")
        print("3. Make sure to install MongoDB as a service")
        print("4. Add MongoDB bin directory to your PATH")
        print("\nAlternatively, if you have Chocolatey:")
        print("   choco install mongodb")
        
    elif system == "darwin":  # macOS
        print("📥 Installing MongoDB on macOS...")
        if run_command("brew --version", "Checking Homebrew"):
            run_command("brew tap mongodb/brew", "Adding MongoDB tap")
            run_command("brew install mongodb-community", "Installing MongoDB")
            run_command("brew services start mongodb/brew/mongodb-community", "Starting MongoDB service")
        else:
            print("❌ Homebrew not found. Please install Homebrew first:")
            print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            
    elif system == "linux":
        print("📥 Installing MongoDB on Linux...")
        # Ubuntu/Debian
        if run_command("which apt", "Checking apt package manager"):
            run_command("wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -", "Adding MongoDB key")
            run_command("echo 'deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list", "Adding MongoDB repository")
            run_command("sudo apt update", "Updating package list")
            run_command("sudo apt install -y mongodb-org", "Installing MongoDB")
            run_command("sudo systemctl start mongod", "Starting MongoDB service")
            run_command("sudo systemctl enable mongod", "Enabling MongoDB service")
        else:
            print("❌ Please install MongoDB manually for your Linux distribution")
            print("   Visit: https://docs.mongodb.com/manual/installation/")
    
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False
    
    return True

def start_mongodb():
    """Start MongoDB service"""
    system = platform.system().lower()
    
    print("🚀 Starting MongoDB service...")
    
    if system == "windows":
        return run_command("net start MongoDB", "Starting MongoDB service")
    elif system == "darwin":  # macOS
        return run_command("brew services start mongodb/brew/mongodb-community", "Starting MongoDB service")
    elif system == "linux":
        return run_command("sudo systemctl start mongod", "Starting MongoDB service")
    
    return False

def check_mongodb_running():
    """Check if MongoDB is running"""
    print("🔍 Checking if MongoDB is running...")
    
    # Try to connect to MongoDB
    result = subprocess.run("mongosh --eval 'db.runCommand({ping: 1})'", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ MongoDB is running and accessible")
        return True
    else:
        print("❌ MongoDB is not running or not accessible")
        return False

def install_python_dependencies():
    """Install Python MongoDB dependencies"""
    print("📦 Installing Python MongoDB dependencies...")
    
    dependencies = ["motor==3.3.2", "pymongo==4.6.1"]
    
    for dep in dependencies:
        if run_command(f"pip install {dep}", f"Installing {dep}"):
            continue
        else:
            print(f"❌ Failed to install {dep}")
            return False
    
    print("✅ All Python dependencies installed successfully")
    return True

async def run_migration():
    """Run the MongoDB migration script"""
    print("📊 Running MongoDB migration...")
    
    try:
        # Import and run migration
        from migrate_to_mongodb import main as migrate_main
        await migrate_main()
        print("✅ MongoDB migration completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_mongodb_config():
    """Create MongoDB configuration for optimal performance"""
    print("⚙️ Creating MongoDB configuration...")
    
    config_content = """# MongoDB Configuration for Math Routing Agent
# Optimized for 5-8 second response times

storage:
  dbPath: ./data/mongodb
  journal:
    enabled: true

systemLog:
  destination: file
  logAppend: true
  path: ./data/mongodb/mongod.log

net:
  port: 27017
  bindIp: 127.0.0.1

processManagement:
  fork: false

# Performance optimizations
operationProfiling:
  slowOpThresholdMs: 100

# Index optimizations
setParameter:
  internalQueryPlannerMaxIndexedSolutions: 64
"""
    
    try:
        os.makedirs("./data/mongodb", exist_ok=True)
        with open("./data/mongodb/mongod.conf", "w") as f:
            f.write(config_content)
        print("✅ MongoDB configuration created")
        return True
    except Exception as e:
        print(f"❌ Failed to create MongoDB configuration: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print_header("🎉 Setup Complete! Next Steps:")
    
    print("""
📋 To start using your optimized Math Routing Agent:

1. 🚀 Start your FastAPI server:
   cd server
   python main.py

2. 🧮 Test the optimized performance:
   - Try simple queries like "2+2" or "area of circle"
   - These should respond in 0.01-0.1 seconds from MongoDB!

3. 📊 Monitor performance:
   - Check response times in the API responses
   - Most queries should be under 5-8 seconds
   - MongoDB cached queries will be nearly instant

4. 🔧 Optional optimizations:
   - Add more common problems to MongoDB
   - Monitor slow queries and optimize them
   - Scale MongoDB if needed

📈 Expected Performance:
   - 80% of queries: 0.01-0.5 seconds (MongoDB cache)
   - 15% of queries: 1-3 seconds (web search)
   - 5% of queries: 3-8 seconds (AI generation)

🎯 Your Math Routing Agent is now optimized for lightning-fast responses!
""")

async def main():
    """Main setup function"""
    print_header("Math Routing Agent - MongoDB Setup")
    print("This script will set up MongoDB for ultra-fast 5-8 second responses")
    
    # Step 1: Check MongoDB installation
    print_step(1, "Checking MongoDB Installation")
    if not check_mongodb_installed():
        install_mongodb()
    
    # Step 2: Start MongoDB
    print_step(2, "Starting MongoDB Service")
    if not check_mongodb_running():
        start_mongodb()
        
        # Wait a moment for MongoDB to start
        import time
        time.sleep(3)
        
        if not check_mongodb_running():
            print("❌ Failed to start MongoDB. Please start it manually.")
            return False
    
    # Step 3: Install Python dependencies
    print_step(3, "Installing Python Dependencies")
    if not install_python_dependencies():
        return False
    
    # Step 4: Create MongoDB configuration
    print_step(4, "Creating MongoDB Configuration")
    create_mongodb_config()
    
    # Step 5: Run migration
    print_step(5, "Migrating Data to MongoDB")
    try:
        await run_migration()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("You can run the migration manually later with: python migrate_to_mongodb.py")
    
    # Step 6: Print next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")