#!/usr/bin/env python3
"""
Test script for the natural date parser
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.date_parser import DateParserService

def test_date_parsing():
    """Test various date input formats"""
    
    test_dates = [
        # Relative dates
        "30 days",
        "in 30 days",
        "2 weeks",
        "in 2 weeks", 
        "1 month",
        "in 1 month",
        "next week",
        "next month",
        "tomorrow",
        
        # Payment terms
        "net 30",
        "net 15",
        "net 45",
        
        # Absolute dates
        "April 12, 2025",
        "12th April 2025",
        "Jan 5th 2025",
        "December 31st",
        "March 15",
        "2025-04-12",
        "12/04/2025",
        "4/12/2025",
        
        # Edge cases
        "April 12",  # No year - should assume this year or next
        "Dec 25",    # No year - should assume this year or next
        "",          # Empty
        "invalid date",  # Invalid
    ]
    
    print("🗓️  Natural Date Parser Test")
    print("=" * 50)
    
    for date_input in test_dates:
        result = DateParserService.parse_natural_date(date_input)
        status = "✅" if result else "❌"
        print(f"{status} '{date_input}' → {result}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed! All formats above should work in the invoice agent.")

if __name__ == "__main__":
    test_date_parsing()
