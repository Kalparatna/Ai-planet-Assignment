"""
JEE Bench Data Loader - Handles loading and processing JEE Bench dataset from HuggingFace
"""

import os
import json
import logging
from typing import Dict, Any, List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from datasets import load_dataset

# Configure logging
logger = logging.getLogger(__name__)

class JEEBenchLoader:
    """Loads and processes JEE Bench dataset from HuggingFace"""
    
    def __init__(self, jee_bench_file: str = "data/jee_bench_data.json"):
        self.jee_bench_file = jee_bench_file
        
        # Subject mapping
        self.subject_mapping = {
            'phy': 'Physics',
            'chem': 'Chemistry', 
            'math': 'Mathematics',
            'maths': 'Mathematics'
        }
    
    def load_jee_bench_data(self) -> List[Document]:
        """Load JEE Bench dataset from Hugging Face"""
        try:
            logger.info("Loading JEE Bench dataset from Hugging Face...")
            
            # Load dataset from Hugging Face
            dataset = load_dataset("daman1209arora/jeebench")
            
            # Process the dataset
            documents = []
            jee_data = []
            total_processed = 0
            
            for split_name, split_data in dataset.items():
                logger.info(f"Processing {split_name} split with {len(split_data)} examples")
                
                for idx, example in enumerate(split_data):
                    try:
                        # Extract fields from the dataset
                        question = example.get('question', '').strip()
                        gold_answer = example.get('gold', '').strip()
                        subject_code = example.get('subject', 'math').strip()
                        question_type = example.get('type', 'MCQ').strip()
                        description = example.get('description', '').strip()
                        
                        # Map subject code to full name
                        subject = self.subject_mapping.get(subject_code, 'Mathematics')
                        
                        # Only process if we have a question
                        if question and len(question) > 20:
                            # Create solution based on gold answer
                            solution = self._create_solution(gold_answer, question_type, description)
                            
                            # Create document content
                            content = f"Problem: {question}\nSolution: {solution}"
                            
                            # Create metadata
                            metadata = {
                                "problem_id": f"jee-{split_name}-{idx}",
                                "category": subject,
                                "topic": f"{subject} - JEE Level",
                                "difficulty": "JEE Level",
                                "source": "JEE Bench Dataset",
                                "split": split_name,
                                "question_type": question_type,
                                "gold_answer": gold_answer
                            }
                            
                            documents.append(Document(page_content=content, metadata=metadata))
                            
                            # Also save to local file for backup
                            jee_data.append({
                                "id": f"jee-{split_name}-{idx}",
                                "problem": question,
                                "solution": solution,
                                "category": subject,
                                "topic": f"{subject} - JEE Level",
                                "difficulty": "JEE Level",
                                "source": "JEE Bench Dataset",
                                "split": split_name,
                                "question_type": question_type,
                                "gold_answer": gold_answer
                            })
                            
                            total_processed += 1
                            
                            # Log progress every 100 items
                            if total_processed % 100 == 0:
                                logger.info(f"Processed {total_processed} valid examples...")
                    
                    except Exception as e:
                        logger.warning(f"Error processing example {idx} in {split_name}: {e}")
                        continue
            
            logger.info(f"Total valid examples processed: {total_processed}")
            
            if total_processed == 0:
                logger.error("No valid examples found in dataset!")
                return []
            
            # Split documents if needed
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
            split_documents = text_splitter.split_documents(documents)
            
            logger.info(f"Created {len(split_documents)} document chunks")
            
            # Save to local file
            with open(self.jee_bench_file, "w", encoding='utf-8') as f:
                json.dump(jee_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(jee_data)} problems to local file: {self.jee_bench_file}")
            
            return split_documents
            
        except Exception as e:
            logger.error(f"Error loading JEE Bench data: {e}")
            # Create empty file if loading fails
            with open(self.jee_bench_file, "w") as f:
                json.dump([], f)
            return []
    
    def _create_solution(self, gold_answer: str, question_type: str, description: str) -> str:
        """Create solution based on gold answer and question type"""
        if gold_answer:
            if question_type == 'MCQ':
                return f"The correct answer is option ({gold_answer}). This is a multiple choice question from {description}."
            elif question_type == 'MCQ(multiple)':
                return f"The correct answers are options ({gold_answer}). This is a multiple choice question with multiple correct answers from {description}."
            else:
                return f"Answer: {gold_answer}. From {description}."
        else:
            return f"This is a {question_type} question from {description}. Please solve step by step."