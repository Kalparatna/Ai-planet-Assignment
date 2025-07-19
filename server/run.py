import uvicorn
import os
import sys
from dotenv import load_dotenv

# Check for virtual environment and dependencies
try:
    import sentence_transformers
except ImportError:
    print("Error: Required packages are not installed.")
    print("Please run the 'start_all.bat' script to set up the environment and start the application.")
    sys.exit(1)

if not hasattr(sys, 'prefix') or sys.prefix == sys.base_prefix:
    print("Error: This script must be run in a virtual environment.")
    print("Please run the 'start_all.bat' script to set up the environment and start the application.")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Get port from environment variable or use default
port = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    print(f"Starting Math Routing Agent server on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)