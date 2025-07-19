import os
import json
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Constants
JEE_BENCH_URL = "https://huggingface.co/datasets/JEE-Bench/JEE-Bench/raw/main/JEE-Bench.json"
RESULTS_FILE = "data/jee_bench_results.json"
API_ENDPOINT = "http://localhost:8000/math/solve"

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

def download_jee_bench():
    """Download the JEE Bench dataset if not already downloaded"""
    if not os.path.exists("data/jee_bench.json"):
        print("Downloading JEE Bench dataset...")
        response = requests.get(JEE_BENCH_URL)
        with open("data/jee_bench.json", "w") as f:
            f.write(response.text)
        print("Download complete!")
    else:
        print("JEE Bench dataset already downloaded.")
    
    # Load the dataset
    with open("data/jee_bench.json", "r") as f:
        return json.load(f)

def evaluate_system(dataset, num_samples=None):
    """Evaluate the Math Routing Agent on the JEE Bench dataset"""
    results = []
    
    # Use a subset of the dataset if specified
    if num_samples and num_samples < len(dataset):
        import random
        dataset = random.sample(dataset, num_samples)
    
    print(f"Evaluating on {len(dataset)} problems from JEE Bench...")
    
    for problem in tqdm(dataset):
        try:
            # Extract problem details
            problem_text = problem.get("problem", "")
            correct_answer = problem.get("answer", "")
            subject = problem.get("subject", "")
            
            # Skip problems without text or answers
            if not problem_text or not correct_answer:
                continue
            
            # Call the Math Routing Agent API
            start_time = time.time()
            response = requests.post(
                API_ENDPOINT,
                json={"query": problem_text}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                solution_data = response.json()
                
                # Extract the solution and source
                solution = solution_data.get("solution", "")
                source = solution_data.get("source", "unknown")
                confidence = solution_data.get("confidence", 0.0)
                
                # Store the result
                result = {
                    "problem": problem_text,
                    "correct_answer": correct_answer,
                    "system_solution": solution,
                    "source": source,
                    "confidence": confidence,
                    "subject": subject,
                    "response_time": end_time - start_time
                }
                results.append(result)
            else:
                print(f"Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"Error processing problem: {e}")
    
    # Save results
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    
    return results

def analyze_results(results):
    """Analyze the benchmark results"""
    if not results:
        print("No results to analyze.")
        return
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(results)
    
    # Overall statistics
    total_problems = len(df)
    avg_response_time = df['response_time'].mean()
    
    # Source distribution
    source_counts = df['source'].value_counts()
    source_percentages = (source_counts / total_problems) * 100
    
    # Subject distribution
    subject_counts = df['subject'].value_counts()
    subject_percentages = (subject_counts / total_problems) * 100
    
    # Confidence analysis
    avg_confidence = df['confidence'].mean()
    confidence_by_source = df.groupby('source')['confidence'].mean()
    confidence_by_subject = df.groupby('subject')['confidence'].mean()
    
    # Print results
    print("\n===== JEE Bench Evaluation Results =====")
    print(f"Total problems evaluated: {total_problems}")
    print(f"Average response time: {avg_response_time:.2f} seconds")
    print(f"Average confidence score: {avg_confidence:.2f}")
    
    print("\n--- Source Distribution ---")
    for source, percentage in source_percentages.items():
        print(f"{source}: {percentage:.1f}% ({source_counts[source]} problems)")
    
    print("\n--- Subject Distribution ---")
    for subject, percentage in subject_percentages.items():
        print(f"{subject}: {percentage:.1f}% ({subject_counts[subject]} problems)")
    
    print("\n--- Average Confidence by Source ---")
    for source, confidence in confidence_by_source.items():
        print(f"{source}: {confidence:.2f}")
    
    print("\n--- Average Confidence by Subject ---")
    for subject, confidence in confidence_by_subject.items():
        print(f"{subject}: {confidence:.2f}")
    
    print("\nDetailed results saved to:", RESULTS_FILE)

def main():
    # Check if the server is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("Error: Math Routing Agent server is not running properly.")
            print("Please start the server using 'python run.py' before running this benchmark.")
            return
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the Math Routing Agent server.")
        print("Please start the server using 'python run.py' before running this benchmark.")
        return
    
    # Download and load the JEE Bench dataset
    dataset = download_jee_bench()
    
    # Ask user for number of samples to evaluate
    try:
        num_samples = int(input(f"Enter number of problems to evaluate (max {len(dataset)}, 0 for all): "))
        if num_samples < 0:
            num_samples = 0
        if num_samples == 0:
            num_samples = None
    except ValueError:
        print("Invalid input. Using 10 samples.")
        num_samples = 10
    
    # Evaluate the system
    results = evaluate_system(dataset, num_samples)
    
    # Analyze the results
    analyze_results(results)

if __name__ == "__main__":
    main()