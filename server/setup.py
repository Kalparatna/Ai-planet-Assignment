import os
import json

# Define the directory structure
directories = [
    'data',
    'middleware',
    'routes',
    'services',
]

# Create the directories if they don't exist
for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

# Create empty JSON files for data storage
data_files = [
    'data/feedback.json',
    'data/improved_solutions.json',
    'data/generated_solutions.json',
    'data/search_history.json',
]

# Create the JSON files with empty arrays if they don't exist
for file_path in data_files:
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)
        print(f"Created file: {file_path}")

print("Setup complete!")