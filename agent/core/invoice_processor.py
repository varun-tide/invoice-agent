"""
Invoice Processor - Core business logic for invoice processing
Single Responsibility: Handle invoice creation workflow
"""

from datetime import datetime
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

try:
    from domain.models import InvoiceData
    from services.date_parser import DateParserService
    from services.description_formatter import DescriptionFormatterService
except ImportError:
    # Fallback for when running from different contexts
    sys.path.insert(0, str(current_dir.parent))
    from agent.domain.models import InvoiceData
    from agent.services.date_parser import DateParserService
    from agent.services.description_formatter import DescriptionFormatterService


class InvoiceProcessor:
    """Handles invoice data processing and validation"""
    
    def __init__(self):
        self.invoice_data = InvoiceData()
    
    def update_invoice_data(self, extracted_data: Dict[str, Any]) -> None:
        """Update the invoice data with extracted information"""
        for field, value in extracted_data.items():
            if value is not None and hasattr(self.invoice_data, field):
                current_value = getattr(self.invoice_data, field)
                if current_value is None:  # Only update if field is currently empty
                    try:
                        if field == 'due_date':
                            # Special handling for due_date - parse natural language
                            parsed_date = DateParserService.parse_natural_date(value)
                            if parsed_date:
                                setattr(self.invoice_data, field, parsed_date)
                                print(f"✅ Parsed date '{value}' as {parsed_date}")
                            else:
                                print(f"❌ Could not parse date '{value}'. Please provide a clearer date format.")
                        elif field == 'invoice_description':
                            # Special handling for invoice_description - format with numbering
                            formatted_description = DescriptionFormatterService.format_description(value)
                            setattr(self.invoice_data, field, formatted_description)
                            if '\n' in formatted_description and '1.' in formatted_description:
                                print(f"✅ Formatted description with automatic numbering")
                        else:
                            setattr(self.invoice_data, field, value)
                    except ValueError as e:
                        print(f"Validation error for {field}: {e}")
    
    def get_missing_fields(self) -> list[str]:
        """Get list of missing required fields"""
        return self.invoice_data.get_missing_fields()
    
    def is_complete(self) -> bool:
        """Check if invoice is complete"""
        return self.invoice_data.is_complete()
    
    def generate_request_message(self, missing_fields: list[str]) -> str:
        """Generate a friendly message requesting missing information"""
        field_mapping = {
            "customer_name": "customer name",
            "customer_email": "customer email address",
            "invoice_description": "description of services/products",
            "total_amount": "total amount",
            "due_date": "due date (e.g., '30 days', 'April 12', 'next week', 'net 30')"
        }
        
        if len(missing_fields) == 1:
            return f"I need the {field_mapping[missing_fields[0]]} to complete your invoice. Could you please provide this information?"
        elif len(missing_fields) == 2:
            return f"I need the {field_mapping[missing_fields[0]]} and {field_mapping[missing_fields[1]]} to complete your invoice."
        else:
            field_list = [field_mapping[field] for field in missing_fields[:-1]]
            return f"I need the following information: {', '.join(field_list)}, and {field_mapping[missing_fields[-1]]}."
    
    def generate_preview(self) -> str:
        """Generate a formatted preview of the invoice"""
        # Format description for better display
        description = self.invoice_data.invoice_description
        if '\n' in description:
            # Multi-line description - indent each line
            description_lines = description.split('\n')
            formatted_description = '\n        ' + '\n        '.join(description_lines)
        else:
            formatted_description = description
        
        preview = f"""
        📧 INVOICE PREVIEW 📧
        
        👤 Customer Information:
        Name: {self.invoice_data.customer_name}
        Email: {self.invoice_data.customer_email}
        
        📝 Invoice Details:
        Description: {formatted_description}
        Amount: ${self.invoice_data.total_amount:.2f}
        Due Date: {self.invoice_data.due_date}
        
        Please review the above information. Reply with:
        - "APPROVE" to create the invoice
        - "EDIT [field]" to modify a specific field (e.g., "EDIT amount")
        - Provide new information to update any field
        """
        return preview
    
    def simulate_api_call(self) -> Dict[str, Any]:
        """
        Simulate an API call to create the invoice
        In a real implementation, this would call your actual invoice API
        """
        # Simulate API response
        invoice_id = f"INV-{datetime.now().strftime('%Y%m%d')}-{hash(str(self.invoice_data)) % 10000:04d}"
        
        api_response = {
            "success": True,
            "invoice_id": invoice_id,
            "status": "created",
            "preview_url": f"https://your-app.com/invoice/{invoice_id}/preview",
            "pdf_url": f"https://your-app.com/invoice/{invoice_id}/pdf",
            "data": self.invoice_data.model_dump()
        }
        
        return api_response
    
    def reset(self) -> None:
        """Reset invoice data for a new invoice"""
        self.invoice_data = InvoiceData()
