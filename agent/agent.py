"""
Main Invoice Agent - Orchestrates all components
Following Clean Architecture: Application layer
"""

from datetime import datetime
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from domain.models import InvoiceData, ResponseMetadata, SessionMetadata
    from core.llm_client import LLMClient
    from core.invoice_processor import InvoiceProcessor
    from services.metadata_service import MetadataService
except ImportError:
    # Fallback for when running from different contexts
    sys.path.insert(0, str(current_dir.parent))
    from agent.domain.models import InvoiceData, ResponseMetadata, SessionMetadata
    from agent.core.llm_client import LLMClient
    from agent.core.invoice_processor import InvoiceProcessor
    from agent.services.metadata_service import MetadataService


class InvoiceAgent:
    """
    Main Invoice Agent that orchestrates invoice creation workflow
    Follows Single Responsibility: Coordinate components, don't implement business logic
    """
    
    def __init__(self, anthropic_api_key: Optional[str] = None, model: str = "claude-opus-4-1-20250805"):
        """Initialize the Invoice Agent with clean separation of concerns"""
        self.llm_client = LLMClient(model, anthropic_api_key)
        self.invoice_processor = InvoiceProcessor()
        self.conversation_history = []
        self.last_response_metadata = ResponseMetadata()
        self.session_metadata = SessionMetadata(session_start_time=datetime.now())
    
    def process_user_input(self, user_input: str) -> str:
        """
        Main method to process user input and return appropriate response
        Orchestrates the workflow without implementing business logic
        """
        self.conversation_history.append(f"User: {user_input}")
        
        # Check if user is approving or editing
        user_input_upper = user_input.upper().strip()
        
        if user_input_upper == "APPROVE":
            return self._handle_approval()
        elif user_input_upper.startswith("EDIT"):
            return self._handle_edit_request()
        else:
            return self._handle_information_extraction(user_input)
    
    def process_user_input_api(self, user_input: str) -> dict:
        """
        API-friendly method that returns structured data instead of formatted strings
        For server/API usage - returns clean JSON without terminal formatting
        """
        self.conversation_history.append(f"User: {user_input}")
        
        # Check if user is approving or editing
        user_input_upper = user_input.upper().strip()
        
        if user_input_upper == "APPROVE":
            return self._handle_approval_api()
        elif user_input_upper.startswith("EDIT"):
            return self._handle_edit_request_api()
        else:
            return self._handle_information_extraction_api(user_input)
    
    def _handle_approval(self) -> str:
        """Handle invoice approval"""
        api_response = self.invoice_processor.simulate_api_call()
        if api_response["success"]:
            response = f"""
                ✅ Invoice Created Successfully!
                
                Invoice ID: {api_response['invoice_id']}
                Status: {api_response['status'].title()}
                
                🔗 Actions Available:
                📄 Preview Invoice: {api_response['preview_url']}
                📥 Download PDF: {api_response['pdf_url']}
                
                Your invoice has been created and is ready to be sent to {self.invoice_processor.invoice_data.customer_name}!
                """
            self.conversation_history.append(f"Assistant: {response}")
            return response
        else:
            return "❌ Sorry, there was an error creating the invoice. Please try again."
    
    def _handle_edit_request(self) -> str:
        """Handle edit requests"""
        return "Please provide the new information for the field you want to edit."
    
    def _handle_information_extraction(self, user_input: str) -> str:
        """Handle information extraction and processing"""
        # Extract information using LLM
        extracted_data, metadata = self.llm_client.extract_information(user_input)
        
        # Update metadata
        self.last_response_metadata = metadata
        MetadataService.update_session_metadata(self.session_metadata, metadata)
        
        # Update invoice data
        self.invoice_processor.update_invoice_data(extracted_data)
        
        # Check for missing fields
        missing_fields = self.invoice_processor.get_missing_fields()
        
        if missing_fields:
            # Request missing information
            response = self.invoice_processor.generate_request_message(missing_fields)
            metadata_display = MetadataService.format_response_metadata(self.last_response_metadata)
            full_response = f"{response}\n{metadata_display}"
            self.conversation_history.append(f"Assistant: {response}")
            return full_response
        else:
            # All information collected, show preview
            response = self.invoice_processor.generate_preview()
            metadata_display = MetadataService.format_response_metadata(self.last_response_metadata)
            full_response = f"{response}\n{metadata_display}"
            self.conversation_history.append(f"Assistant: {response}")
            return full_response
    
    def _handle_approval_api(self) -> dict:
        """Handle invoice approval - API version"""
        api_response = self.invoice_processor.simulate_api_call()
        if api_response["success"]:
            return {
                "success": True,
                "action": "invoice_created",
                "message": f"Invoice {api_response['invoice_id']} created successfully",
                "invoice_status": "created",
                "invoice": {
                    "invoice_id": api_response['invoice_id'],
                    "invoice_number": api_response['invoice_id'],
                    "status": api_response['status'],
                    "customer_name": self.invoice_processor.invoice_data.customer_name,
                    "customer_email": self.invoice_processor.invoice_data.customer_email,
                    "description": self.invoice_processor.invoice_data.invoice_description,
                    "amount": self.invoice_processor.invoice_data.total_amount,
                    "due_date": self.invoice_processor.invoice_data.due_date,
                    "preview_url": api_response['preview_url'],
                    "pdf_url": api_response['pdf_url']
                }
            }
        else:
            return {
                "success": False,
                "action": "invoice_creation_failed",
                "message": "Error creating the invoice. Please try again.",
                "invoice_status": "failed",
                "error": "Invoice creation failed"
            }
    
    def _handle_edit_request_api(self) -> dict:
        """Handle edit requests - API version"""
        return {
            "success": True,
            "action": "edit_request",
            "message": "Please provide the new information for the field you want to edit.",
            "invoice_status": "editing",
            "current_data": self.invoice_processor.invoice_data.model_dump()
        }
    
    def _handle_information_extraction_api(self, user_input: str) -> dict:
        """Handle information extraction and processing - API version"""
        # Extract information using LLM
        extracted_data, metadata = self.llm_client.extract_information(user_input)
        
        # Update metadata
        self.last_response_metadata = metadata
        MetadataService.update_session_metadata(self.session_metadata, metadata)
        
        # Update invoice data
        self.invoice_processor.update_invoice_data(extracted_data)
        
        # Check for missing fields
        missing_fields = self.invoice_processor.get_missing_fields()
        
        if missing_fields:
            # Request missing information
            message = self.invoice_processor.generate_request_message(missing_fields)
            return {
                "success": True,
                "action": "collecting_information",
                "message": message,
                "invoice_status": "incomplete",
                "missing_fields": missing_fields,
                "current_data": self.invoice_processor.invoice_data.model_dump(),
                "extracted_data": extracted_data
            }
        else:
            # All information collected, ready for approval
            return {
                "success": True,
                "action": "ready_for_approval",
                "message": "All information collected. Please review and approve the invoice.",
                "invoice_status": "complete",
                "missing_fields": [],
                "invoice_data": self.invoice_processor.invoice_data.model_dump(),
                "preview": {
                    "customer_name": self.invoice_processor.invoice_data.customer_name,
                    "customer_email": self.invoice_processor.invoice_data.customer_email,
                    "description": self.invoice_processor.invoice_data.invoice_description,
                    "amount": self.invoice_processor.invoice_data.total_amount,
                    "due_date": self.invoice_processor.invoice_data.due_date
                }
            }
    
    # Properties to maintain backward compatibility
    @property
    def invoice_data(self) -> InvoiceData:
        """Access to invoice data for backward compatibility"""
        return self.invoice_processor.invoice_data
    
    def get_missing_fields(self) -> list[str]:
        """Get missing fields (for backward compatibility)"""
        return self.invoice_processor.get_missing_fields()
    
    def get_last_response_metadata(self) -> ResponseMetadata:
        """Get the metadata from the last API call"""
        return self.last_response_metadata
    
    def get_session_metadata(self) -> SessionMetadata:
        """Get the cumulative session metadata"""
        return self.session_metadata
    
    def get_formatted_metadata(self) -> str:
        """Get formatted metadata string for the last response"""
        return MetadataService.format_response_metadata(self.last_response_metadata)
    
    def get_formatted_session_metadata(self) -> str:
        """Get formatted session metadata string"""
        return MetadataService.format_session_metadata(self.session_metadata)
    
    def reset(self) -> None:
        """Reset the agent for a new invoice"""
        self.invoice_processor.reset()
        self.conversation_history = []
        self.last_response_metadata = ResponseMetadata()
    
    def reset_session(self) -> None:
        """Reset the entire session including metadata"""
        self.invoice_processor.reset()
        self.conversation_history = []
        self.last_response_metadata = ResponseMetadata()
        self.session_metadata = SessionMetadata(session_start_time=datetime.now())
