"""
Date Parser Service - Natural language date processing
Single Responsibility: Handle date parsing logic
"""

import re
from datetime import datetime, timedelta
from typing import Optional
from dateutil import parser as date_parser


class DateParserService:
    """Service for parsing natural language dates"""
    
    @staticmethod
    def parse_natural_date(date_input: str) -> Optional[str]:
        """
        Parse natural language date input and convert to YYYY-MM-DD format
        Handles: "30 days", "1 week", "April 12 2025", "Jan 5th 2025", etc.
        """
        if not date_input or not isinstance(date_input, str):
            return None
            
        date_input = date_input.strip().lower()
        today = datetime.now()
        
        try:
            # Handle relative dates first
            
            # "in X days" or "X days"
            days_match = re.search(r'(?:in\s+)?(\d+)\s*days?', date_input)
            if days_match:
                days = int(days_match.group(1))
                target_date = today + timedelta(days=days)
                return target_date.strftime('%Y-%m-%d')
            
            # "in X weeks" or "X weeks"
            weeks_match = re.search(r'(?:in\s+)?(\d+)\s*weeks?', date_input)
            if weeks_match:
                weeks = int(weeks_match.group(1))
                target_date = today + timedelta(weeks=weeks)
                return target_date.strftime('%Y-%m-%d')
            
            # "in X months" or "X months"
            months_match = re.search(r'(?:in\s+)?(\d+)\s*months?', date_input)
            if months_match:
                months = int(months_match.group(1))
                target_date = today + timedelta(days=months * 30)
                return target_date.strftime('%Y-%m-%d')
            
            # "next week"
            if 'next week' in date_input:
                target_date = today + timedelta(weeks=1)
                return target_date.strftime('%Y-%m-%d')
            
            # "next month"
            if 'next month' in date_input:
                target_date = today + timedelta(days=30)
                return target_date.strftime('%Y-%m-%d')
            
            # "tomorrow"
            if 'tomorrow' in date_input:
                target_date = today + timedelta(days=1)
                return target_date.strftime('%Y-%m-%d')
            
            # Handle payment terms like "net 30", "net 15"
            net_match = re.search(r'net\s*(\d+)', date_input)
            if net_match:
                days = int(net_match.group(1))
                target_date = today + timedelta(days=days)
                return target_date.strftime('%Y-%m-%d')
            
            # Try to parse as absolute date using dateutil
            cleaned_input = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_input)
            parsed_date = date_parser.parse(cleaned_input, fuzzy=True)
            
            # If the parsed date is in the past and no year was specified, assume next year
            if parsed_date.year == today.year and parsed_date.date() < today.date():
                parsed_date = parsed_date.replace(year=today.year + 1)
            
            return parsed_date.strftime('%Y-%m-%d')
            
        except (ValueError, TypeError, OverflowError) as e:
            print(f"Date parsing error for '{date_input}': {e}")
            return None
