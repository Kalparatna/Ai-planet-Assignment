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
        pass
    
    def format_for_ui(self, solution: str, problem: str = None) -> Dict[str, Any]:
        """Format solution for UI display with proper structure"""
        
        # Clean and structure the solution
        formatted_solution = self._clean_and_structure(solution)
        
        # Extract problem if not provided
        if not problem:
            problem = self._extract_problem(formatted_solution)
        
        # Parse the solution into structured sections
        sections = self._parse_into_sections(formatted_solution)
        
        # Format the final response
        return {
            "problem": self._format_problem(problem),
            "solution": self._format_solution_content(formatted_solution),
            "sections": sections,
            "formatted": True,
            "display_type": "structured",
            "supports_math": True
        }
    
    def _clean_and_structure(self, text: str) -> str:
        """Clean and structure the content"""
        if not text:
            return ""
        
        # Extract content from LangChain response format
        text = self._extract_langchain_content(text)
        
        # Remove HTML entities
        text = html.unescape(text)
        
        # Clean HTML tags but preserve content
        text = self._clean_html_tags(text)
        
        # Clean up formatting artifacts
        text = self._clean_formatting_artifacts(text)
        
        # Clean up whitespace
        text = self._clean_whitespace(text)
        
        return text
    
    def _extract_langchain_content(self, text: str) -> str:
        """Extract actual content from LangChain response format"""
        
        # Handle content='...' format
        content_match = re.search(r"content='([^']*(?:\\'[^']*)*)'", text)
        if content_match:
            content = content_match.group(1)
            content = content.replace("\\'", "'")
            content = content.replace("\\n", "\n")
            return content
        
        # Handle content="..." format
        content_match = re.search(r'content="([^"]*(?:\\"[^"]*)*)"', text)
        if content_match:
            content = content_match.group(1)
            content = content.replace('\\"', '"')
            content = content.replace("\\n", "\n")
            return content
        
        # Remove metadata patterns
        text = re.sub(r'additional_kwargs=\{[^}]*\}', '', text)
        text = re.sub(r'response_metadata=\{[^}]*\}', '', text)
        text = re.sub(r'id=[\'"][^\'"]*[\'"]', '', text)
        text = re.sub(r'usage_metadata=\{[^}]*\}', '', text)
        
        return text
    
    def _clean_html_tags(self, text: str) -> str:
        """Remove HTML tags while preserving content"""
        
        # Handle superscript and subscript
        text = re.sub(r'<sup>([^<]+)</sup>', r'^\1', text)
        text = re.sub(r'<sub>([^<]+)</sub>', r'_\1', text)
        
        # Handle bold and italic
        text = re.sub(r'<b>([^<]+)</b>', r'\1', text)
        text = re.sub(r'<strong>([^<]+)</strong>', r'\1', text)
        text = re.sub(r'<i>([^<]+)</i>', r'\1', text)
        text = re.sub(r'<em>([^<]+)</em>', r'\1', text)
        
        # Handle line breaks
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<p>', '\n', text)
        text = re.sub(r'</p>', '\n', text)
        
        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        return text
    
    def _clean_formatting_artifacts(self, text: str) -> str:
        """Clean up common formatting artifacts"""
        
        # Remove excessive asterisks and formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        
        # Clean up step numbering
        text = re.sub(r'^\*\*Step \d+:\*\*\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\*\*\d+\.\s*', '', text, flags=re.MULTILINE)
        
        # Remove "Problem:" prefixes that appear mid-text
        text = re.sub(r'Problem:\s*', '', text, flags=re.IGNORECASE)
        
        return text
    
    def _clean_whitespace(self, text: str) -> str:
        """Clean up excessive whitespace"""
        
        # Remove multiple consecutive newlines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in text.split('\n')]
        
        # Remove empty lines at start and end
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        return '\n'.join(lines)
    
    def _parse_into_sections(self, text: str) -> List[Dict[str, Any]]:
        """Parse text into structured sections for UI rendering"""
        
        lines = text.split('\n')
        sections = []
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_content:
                    current_content.append("")
                continue
            
            # Check if this is a header/section
            section_type = self._identify_section_type(line)
            
            if section_type:
                # Save previous section
                if current_section:
                    sections.append({
                        "type": current_section["type"],
                        "title": current_section["title"],
                        "content": self._format_section_content(current_content, current_section["type"])
                    })
                
                # Start new section
                current_section = {
                    "type": section_type,
                    "title": self._clean_section_title(line)
                }
                current_content = []
            else:
                # Add to current section content
                current_content.append(line)
        
        # Add final section
        if current_section:
            sections.append({
                "type": current_section["type"],
                "title": current_section["title"],
                "content": self._format_section_content(current_content, current_section["type"])
            })
        
        return sections
    
    def _identify_section_type(self, line: str) -> str:
        """Identify the type of section based on the line"""
        
        line_lower = line.lower()
        
        # Main headers
        if any(header in line_lower for header in ['pythagorean theorem', 'definition', 'theorem']):
            return "header"
        
        # Steps
        if re.match(r'^\d+\.\s*step|^step\s*\d+', line_lower) or \
           re.match(r'^\d+\.\s*[a-z][a-z\s]*:', line_lower):
            return "step"
        
        # Examples
        if 'example' in line_lower:
            return "example"
        
        # Formulas (standalone mathematical expressions)
        if self._is_formula_line(line):
            return "formula"
        
        # Sub-headers
        if re.match(r'^\d+\.\s*[A-Z]', line) or \
           (line.startswith('**') and line.endswith('**')):
            return "subheader"
        
        return None
    
    def _is_formula_line(self, line: str) -> bool:
        """Check if line is a mathematical formula"""
        
        # Must be relatively short and contain math symbols
        if len(line) > 50:
            return False
        
        math_indicators = ['=', '²', '³', '√', '+', '-', '^']
        math_count = sum(1 for indicator in math_indicators if indicator in line)
        
        # Check for common formula patterns
        formula_patterns = [
            r'^[a-z]²\s*\+\s*[a-z]²\s*=\s*[a-z]²$',  # a² + b² = c²
            r'^[a-z]\s*=\s*√\d+\s*=\s*\d+$',          # c = √25 = 5
            r'^\d+²\s*\+\s*\d+²\s*=\s*\d+$',          # 3² + 4² = 25
        ]
        
        for pattern in formula_patterns:
            if re.match(pattern, line.strip()):
                return True
        
        return math_count >= 2 and len(line.split()) <= 8
    
    def _clean_section_title(self, line: str) -> str:
        """Clean section title"""
        # Remove asterisks, numbers, and colons
        cleaned = re.sub(r'^\*\*|\*\*$', '', line)
        cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
        cleaned = re.sub(r':$', '', cleaned)
        return cleaned.strip()
    
    def _format_section_content(self, content_lines: List[str], section_type: str) -> List[Dict[str, Any]]:
        """Format section content based on type"""
        
        formatted_content = []
        
        for line in content_lines:
            if not line.strip():
                continue
            
            content_item = {
                "type": "text",
                "content": line.strip()
            }
            
            # Special formatting based on content
            if self._is_formula_line(line):
                content_item["type"] = "formula"
                content_item["content"] = self._format_math_expression(line.strip())
            elif line.strip().startswith(('•', '-', '*')):
                content_item["type"] = "list_item"
                content_item["content"] = re.sub(r'^[•\-*]\s*', '', line.strip())
            elif re.match(r'^\d+\.\s', line.strip()):
                content_item["type"] = "numbered_item"
                content_item["content"] = line.strip()
            
            formatted_content.append(content_item)
        
        return formatted_content
    
    def _format_math_expression(self, expression: str) -> str:
        """Format mathematical expressions for display"""
        
        # Convert common math notation
        expression = re.sub(r'([a-z])²', r'\1²', expression)
        expression = re.sub(r'([a-z])³', r'\1³', expression)
        expression = re.sub(r'\^2', '²', expression)
        expression = re.sub(r'\^3', '³', expression)
        
        return expression
    
    def _extract_problem(self, text: str) -> str:
        """Extract the problem statement"""
        
        lines = text.split('\n')
        for line in lines:
            if line.lower().startswith('problem:'):
                return line.replace('Problem:', '').strip()
        
        # Try to find first meaningful line
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
        return problem
    
    def _format_solution_content(self, solution: str) -> str:
        """Format the solution content for display"""
        return solution
    
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
            'sections': formatted.get('sections', []),
            'formatted': True,
            'display_ready': True,
            'display_type': 'structured',
            'supports_math': True
        })
        
        return response_data