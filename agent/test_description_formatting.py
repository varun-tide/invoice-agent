#!/usr/bin/env python3
"""
Test script for description formatting with automatic numbering
"""

from services.description_formatter import DescriptionFormatterService

def test_description_formatting():
    """Test various description input formats"""
    
    test_descriptions = [
        # Comma-separated
        "Web development, Logo design, Content creation",
        
        # Semicolon-separated
        "Frontend development; Backend API; Database setup; Testing",
        
        # Line break separated
        "Mobile app development\nUI/UX design\nApp store deployment",
        
        # Bullet points
        "• Website redesign\n• SEO optimization\n• Social media setup",
        
        # Dash separated
        "- Custom WordPress theme\n- Plugin development\n- Site migration",
        
        # Mixed with existing numbering (should be cleaned)
        "1. Logo design, 2) Business cards, 3- Website banner",
        
        # Single item (should remain unchanged)
        "Complete website development project",
        
        # Pipe separated
        "Product photography | Image editing | Catalog creation",
        
        # Asterisk separated
        "* Market research\n* Strategy development\n* Implementation plan\n* Performance analysis",
        
        # Complex mixed format
        "Web development (frontend and backend), Database design; API integration, Testing and deployment",
    ]
    
    print("📝 Description Formatting Test")
    print("=" * 60)
    
    for i, description in enumerate(test_descriptions, 1):
        formatted = DescriptionFormatterService.format_description(description)
        
        print(f"\n{i}. TEST INPUT:")
        print(f"   '{description}'")
        print(f"   OUTPUT:")
        if '\n' in formatted:
            for line in formatted.split('\n'):
                print(f"   {line}")
        else:
            print(f"   '{formatted}'")
        print("-" * 60)
    
    print("\n✅ All description formats tested!")
    print("\nExample in context:")
    print("User: 'I need an invoice for web development, logo design, and content creation for $2500'")
    print("Agent will format description as:")
    print("1. Web development")
    print("2. Logo design") 
    print("3. Content creation")

if __name__ == "__main__":
    test_description_formatting()
