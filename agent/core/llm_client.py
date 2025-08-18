"""
LLM Client - Handles communication with Anthropic API
Single Responsibility: Manage LLM interactions
"""

import json
import time
import sys
import random
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
    
    def _retry_with_backoff(self, func, max_retries: int = 3, base_delay: float = 1.0):
        """
        Retry a function with exponential backoff for handling API rate limits and overload errors
        """
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                error_str = str(e).lower()
                
                # Check for specific error conditions that warrant retry
                should_retry = (
                    "overloaded" in error_str or
                    "529" in error_str or
                    "rate limit" in error_str or
                    "too many requests" in error_str or
                    "503" in error_str or  # Service unavailable
                    "502" in error_str or  # Bad gateway
                    "timeout" in error_str
                )
                
                if should_retry and attempt < max_retries - 1:
                    # Calculate delay with exponential backoff + jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"🔄 API temporarily unavailable (attempt {attempt + 1}/{max_retries}). Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    # Re-raise the exception if we've exhausted retries or it's not retryable
                    raise e
        
        return None
    
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
            # Record overall start time (includes retries)
            overall_start_time = time.time()
            
            # Track actual API call time separately
            api_call_time_ms = 0
            
            # Use retry wrapper for the API call
            def make_api_call():
                nonlocal api_call_time_ms
                api_start = time.time()
                result = self.llm.invoke(extraction_prompt)
                api_end = time.time()
                api_call_time_ms = int((api_end - api_start) * 1000)
                return result
            
            response = self._retry_with_backoff(make_api_call, max_retries=3, base_delay=2.0)
            
            # Use the actual API call time for metadata (not including retry delays)
            response_time_ms = api_call_time_ms
            
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
            # Return the metadata we captured even if JSON parsing failed
            if 'metadata' in locals():
                return {}, metadata
            else:
                return {}, ResponseMetadata()
        except Exception as e:
            error_str = str(e)
            # Try to extract metadata even from failed requests if we have response data
            metadata = ResponseMetadata()
            try:
                if 'response' in locals() and response:
                    # Use the API call time if available, otherwise calculate from overall time
                    if 'api_call_time_ms' in locals() and api_call_time_ms > 0:
                        response_time_ms = api_call_time_ms
                    else:
                        end_time = time.time()
                        response_time_ms = int((end_time - overall_start_time) * 1000) if 'overall_start_time' in locals() else 0
                    metadata = MetadataService.extract_metadata_from_response(
                        response, response_time_ms, self.model
                    )
            except:
                pass  # If metadata extraction fails, use empty metadata
            
            if "overloaded" in error_str.lower() or "529" in error_str:
                print(f"⚠️  Anthropic servers are temporarily overloaded. This is not an issue with your code.")
                print(f"   Please try again in a few minutes. Error: {e}")
            elif "rate limit" in error_str.lower():
                print(f"⚠️  Rate limit exceeded. Please wait a moment before trying again. Error: {e}")
            elif "authentication" in error_str.lower() or "api_key" in error_str.lower():
                print(f"🔑 Authentication error. Please check your ANTHROPIC_API_KEY in .env file. Error: {e}")
            else:
                print(f"❌ Error extracting information: {e}")
            return {}, metadata
