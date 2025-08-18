"""
LLM Client - Handles communication with Anthropic API
Single Responsibility: Manage LLM interactions
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

try:
    from domain.models import ResponseMetadata
    from services.metadata_service import MetadataService
except ImportError:
    # Fallback for when running from different contexts
    sys.path.insert(0, str(current_dir.parent))
    from agent.domain.models import ResponseMetadata
    from agent.services.metadata_service import MetadataService


class LLMClient:
    """Client for interacting with Anthropic's Claude API"""
    
    def __init__(self, model: str = "claude-opus-4-1-20250805", anthropic_api_key: Optional[str] = None):
        """Initialize the LLM client"""
        self.model = model
        if anthropic_api_key:
            self.llm = ChatAnthropic(model=model, anthropic_api_key=anthropic_api_key)
        else:
            self.llm = ChatAnthropic(model=model)
    
    def extract_information(self, user_input: str) -> Dict[str, Any]:
        """
        Extract invoice information from user input using Claude
        """
        extraction_prompt = f"""
        You are an expert at extracting invoice information from text. 
        Analyze the following user input and extract any invoice-related information:
        
        User Input: "{user_input}"
        
        Extract and return ONLY a JSON object with the following fields (use null for missing information):
        {{
            "customer_name": "extracted customer name",
            "customer_email": "extracted email address",
            "invoice_description": "extracted description/service details",
            "total_amount": extracted_amount_as_number,
            "due_date": "extracted date in YYYY-MM-DD format"
        }}
        
        Important guidelines:
        - For amounts, extract only the numeric value (e.g., from "$500" extract 500)
        - For dates, extract the raw date text as provided by user (e.g., "30 days", "April 12 2025", "next week", "net 30")
        - For descriptions, capture ALL services/products mentioned, including multiple items separated by commas, semicolons, or line breaks
        - Do NOT convert dates to YYYY-MM-DD format - return the original text
        - Return null for any field that cannot be confidently extracted
        - Do not include any text outside the JSON object
        - Response must be valid JSON only
        """
        
        try:
            # Record start time
            start_time = time.time()
            
            response = self.llm.invoke(extraction_prompt)
            
            # Record end time and calculate duration
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Extract metadata
            metadata = MetadataService.extract_metadata_from_response(
                response, response_time_ms, self.model
            )
            
            # Check if response exists and has content
            if not response or not hasattr(response, 'content') or not response.content:
                print("Error extracting information: Empty response from LLM")
                return {}, metadata
            
            response_content = response.content.strip()
            
            if not response_content:
                print("Error extracting information: Empty response content")
                return {}, metadata
            
            # Try to find JSON in the response
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                print("Error extracting information: No JSON found in response")
                print(f"Response content: {response_content}")
                return {}, metadata
            
            json_content = response_content[json_start:json_end]
            extracted_data = json.loads(json_content)
            
            # Validate that it's a dictionary
            if not isinstance(extracted_data, dict):
                print("Error extracting information: Response is not a JSON object")
                return {}, metadata
                
            return extracted_data, metadata
            
        except json.JSONDecodeError as e:
            print(f"Error extracting information: Invalid JSON - {e}")
            print(f"Response content: {response.content if response else 'No response'}")
            return {}, ResponseMetadata()
        except Exception as e:
            print(f"Error extracting information: {e}")
            return {}, ResponseMetadata()
