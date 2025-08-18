"""
Description Formatter Service - Format invoice descriptions
Single Responsibility: Handle description formatting logic
"""

import re


class DescriptionFormatterService:
    """Service for formatting invoice descriptions"""
    
    @staticmethod
    def format_description(description: str) -> str:
        """
        Format description with automatic numbering for multiple items
        """
        if not description:
            return description
            
        # Check if description contains multiple items (common separators)
        separators = ['\n', ';', ',', '|', '•', '-', '*']
        
        # Find the best separator
        best_separator = None
        max_parts = 1
        
        for sep in separators:
            if sep in description:
                parts = [part.strip() for part in description.split(sep) if part.strip()]
                if len(parts) > max_parts:
                    max_parts = len(parts)
                    best_separator = sep
        
        # If we found multiple items, format with numbering
        if best_separator and max_parts > 1:
            parts = [part.strip() for part in description.split(best_separator) if part.strip()]
            
            # Remove any existing numbering to avoid duplication
            cleaned_parts = []
            for part in parts:
                # Remove common numbering patterns
                part = re.sub(r'^\d+[\.\)\-\s]+', '', part.strip())
                part = re.sub(r'^[•\-\*]\s*', '', part.strip())
                if part:
                    cleaned_parts.append(part)
            
            # Add professional numbering
            if len(cleaned_parts) > 1:
                numbered_items = [f"{i+1}. {item}" for i, item in enumerate(cleaned_parts)]
                return '\n'.join(numbered_items)
        
        return description
