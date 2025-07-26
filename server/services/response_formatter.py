#!/usr/bin/env python3
"""
Response formatter service to properly format mathematical solutions for UI display
"""

import re
import html
from typing import Dict, Any, List

class ResponseFormatter:
    """Format mathematical solutions for proper UI display"""
    
    def __init__(self):
        self.math_symbols = {
            '²': '^2',
            '³': '^3',
            '⁴': '^4',
            '⁵': '^5',
            '⁶': '^6',
            '⁷': '^7',
            '⁸': '^8',
            '⁹': '^9',
            '₁': '_1',
            '₂': '_2',
            '₃': '_3',
            '₄': '_4',
            '₅': '_5',
            'π': 'π',
            '∞': '∞',
            '≈': '≈',
            '≠': '≠',
            '≤': '≤',
            '≥': '≥',
            '±': '±',
            '∑': 'Σ',
            '∫': '∫',
            '∂': '∂',
            '√': '√',
            'α': 'α',
            'β': 'β',
            'γ': 'γ',
            'δ': 'δ',
            'θ': 'θ',
            'λ': 'λ',
            'μ': 'μ',
            'σ': 'σ',
            'φ': 'φ',
            'ω': 'ω'
        }
    
    def format_for_ui(self, solution: str, problem: str = None) -> Dict[str, Any]:
        """Format solution for UI display with proper structure"""
        
        # Clean and structure the solution
        formatted_solution = self._clean_and_structure(solution)
        
        # Extract problem if not provided
        if not problem:
            problem = self._extract_problem(formatted_solution)
        
        # Format the final response
        return {
            "problem": self._format_problem(problem),
            "solution": self._format_solution_content(formatted_solution),
            "formatted": True,
            "display_type": "structured"
        }
    
    def _clean_and_structure(self, text: str) -> str:
        """Clean HTML tags and structure the content"""
        if not text:
            return ""
        
        # First, extract content from LangChain response format
        text = self._extract_langchain_content(text)
        
        # Remove HTML entities
        text = html.unescape(text)
        
        # Clean HTML tags but preserve content
        text = self._clean_html_tags(text)
        
        # Fix mathematical notation
        text = self._fix_math_notation(text)
        
        # Structure the content
        text = self._structure_content(text)
        
        # Clean up whitespace
        text = self._clean_whitespace(text)
        
        return text
    
    def _extract_langchain_content(self, text: str) -> str:
        """Extract actual content from LangChain response format"""
        
        # Handle the case where we have content='...' format
        content_match = re.search(r"content='([^']*(?:\\'[^']*)*)'", text)
        if content_match:
            # Extract the content and unescape quotes
            content = content_match.group(1)
            content = content.replace("\\'", "'")
            content = content.replace("\\n", "\n")
            return content
        
        # Handle the case where we have content="..." format
        content_match = re.search(r'content="([^"]*(?:\\"[^"]*)*)"', text)
        if content_match:
            # Extract the content and unescape quotes
            content = content_match.group(1)
            content = content.replace('\\"', '"')
            content = content.replace("\\n", "\n")
            return content
        
        # Remove metadata patterns
        text = re.sub(r'additional_kwargs=\{[^}]*\}', '', text)
        text = re.sub(r'response_metadata=\{[^}]*\}', '', text)
        text = re.sub(r'id=[\'"][^\'"]*[\'"]', '', text)
        text = re.sub(r'usage_metadata=\{[^}]*\}', '', text)
        
        # Remove any remaining patterns like "### Step 1content='"
        text = re.sub(r'###\s*Step\s*\d+content=', '### Step ', text)
        
        return text
    
    def _clean_html_tags(self, text: str) -> str:
        """Remove HTML tags while preserving mathematical content"""
        
        # Handle superscript and subscript
        text = re.sub(r'<sup>([^<]+)</sup>', r'^(\1)', text)
        text = re.sub(r'<sub>([^<]+)</sub>', r'_(\1)', text)
        
        # Handle bold and italic
        text = re.sub(r'<b>([^<]+)</b>', r'**\1**', text)
        text = re.sub(r'<strong>([^<]+)</strong>', r'**\1**', text)
        text = re.sub(r'<i>([^<]+)</i>', r'*\1*', text)
        text = re.sub(r'<em>([^<]+)</em>', r'*\1*', text)
        
        # Handle line breaks
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<p>', '\n', text)
        text = re.sub(r'</p>', '\n', text)
        
        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        return text
    
    def _fix_math_notation(self, text: str) -> str:
        """Fix mathematical notation for better display"""
        
        # Replace Unicode math symbols
        for unicode_char, replacement in self.math_symbols.items():
            text = text.replace(unicode_char, replacement)
        
        # Fix common mathematical expressions
        text = re.sub(r'x\^2', 'x²', text)
        text = re.sub(r'x\^3', 'x³', text)
        text = re.sub(r'x\^4', 'x⁴', text)
        text = re.sub(r'\^2', '²', text)
        text = re.sub(r'\^3', '³', text)
        
        # Fix fractions (simple ones)
        text = re.sub(r'(\d+)/(\d+)', r'\1/\2', text)
        
        # Fix derivatives
        text = re.sub(r"f'", "f'", text)
        text = re.sub(r'd/dx', 'd/dx', text)
        
        return text
    
    def _structure_content(self, text: str) -> str:
        """Structure the content with proper sections"""
        
        # Split into lines for processing
        lines = text.split('\n')
        structured_lines = []
        
        current_section = None
        step_counter = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify sections
            if line.lower().startswith('problem:'):
                current_section = 'problem'
                structured_lines.append(f"## Problem\n{line.replace('Problem:', '').strip()}")
            elif line.lower().startswith('solution:'):
                current_section = 'solution'
                structured_lines.append("## Solution")
            elif self._is_step_line(line):
                step_counter += 1
                structured_lines.append(f"### Step {step_counter}")
                structured_lines.append(line)
            elif line.startswith('**') and line.endswith('**'):
                # This is a header
                structured_lines.append(f"### {line.replace('**', '')}")
            else:
                # Regular content
                structured_lines.append(line)
        
        return '\n\n'.join(structured_lines)
    
    def _is_step_line(self, line: str) -> bool:
        """Check if a line represents a step"""
        step_indicators = [
            'step', 'first', 'next', 'then', 'finally', 'therefore',
            'now', 'let', 'we', 'apply', 'using', 'substitute'
        ]
        
        line_lower = line.lower()
        return any(indicator in line_lower for indicator in step_indicators) and len(line) > 20
    
    def _clean_whitespace(self, text: str) -> str:
        """Clean up excessive whitespace"""
        
        # Remove multiple consecutive newlines
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in text.split('\n')]
        
        # Remove empty lines at start and end
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        return '\n'.join(lines)
    
    def _extract_problem(self, text: str) -> str:
        """Extract the problem statement from the solution"""
        
        lines = text.split('\n')
        for line in lines:
            if line.lower().startswith('problem:') or line.startswith('## Problem'):
                return line.replace('Problem:', '').replace('## Problem', '').strip()
        
        # If no explicit problem found, try to extract from first meaningful line
        for line in lines:
            if len(line.strip()) > 10 and not line.startswith('#'):
                return line.strip()
        
        return "Mathematical Problem"
    
    def _format_problem(self, problem: str) -> str:
        """Format the problem statement"""
        if not problem:
            return "Mathematical Problem"
        
        # Clean the problem statement
        problem = problem.replace('**Problem:**', '').strip()
        problem = self._fix_math_notation(problem)
        
        return problem
    
    def _format_solution_content(self, solution: str) -> str:
        """Format the solution content for display"""
        
        # Remove problem section if it exists
        lines = solution.split('\n')
        solution_lines = []
        in_solution = False
        
        for line in lines:
            if line.startswith('## Solution') or line.lower().startswith('solution:'):
                in_solution = True
                continue
            elif line.startswith('## Problem'):
                in_solution = False
                continue
            elif in_solution or (not line.startswith('## Problem') and line.strip()):
                solution_lines.append(line)
        
        formatted_solution = '\n'.join(solution_lines).strip()
        
        # If no solution section found, use the whole text
        if not formatted_solution:
            formatted_solution = solution
        
        return formatted_solution
    
    def format_api_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the complete API response for UI consumption"""
        
        solution = response_data.get('solution', '')
        problem = response_data.get('problem', '')
        
        # Format the solution
        formatted = self.format_for_ui(solution, problem)
        
        # Update the response
        response_data.update({
            'solution': formatted['solution'],
            'problem': formatted['problem'],
            'formatted': True,
            'display_ready': True
        })
        
        return response_data