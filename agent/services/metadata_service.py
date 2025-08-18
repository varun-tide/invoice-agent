"""
Metadata Service - Handle API usage tracking and cost calculation
Single Responsibility: Manage metadata operations
"""

from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

try:
    from domain.models import ResponseMetadata, SessionMetadata
except ImportError:
    # Fallback for when running from different contexts
    sys.path.insert(0, str(current_dir.parent))
    from agent.domain.models import ResponseMetadata, SessionMetadata


class MetadataService:
    """Service for managing API metadata and costs"""
    
    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "claude-opus-4-1-20250805": {
            "input": 15.00,  # $15 per 1M input tokens
            "output": 75.00  # $75 per 1M output tokens
        },
        "claude-3-sonnet-20240229": {
            "input": 3.00,   # $3 per 1M input tokens
            "output": 15.00  # $15 per 1M output tokens
        },
        "claude-3-haiku-20240307": {
            "input": 0.25,   # $0.25 per 1M input tokens
            "output": 1.25   # $1.25 per 1M output tokens
        }
    }
    
    @classmethod
    def calculate_cost(cls, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate the cost in USD based on token usage"""
        if model not in cls.PRICING:
            return 0.0
        
        pricing = cls.PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
    
    @classmethod
    def extract_metadata_from_response(cls, response, response_time_ms: int, model: str) -> ResponseMetadata:
        """Extract metadata from the LLM response"""
        metadata = ResponseMetadata()
        metadata.model = model
        metadata.response_time_ms = response_time_ms
        
        # Extract token usage from response
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            metadata.input_tokens = usage.get('input_tokens', 0)
            metadata.output_tokens = usage.get('output_tokens', 0)
            
            if 'input_token_details' in usage:
                token_details = usage['input_token_details']
                metadata.cached_tokens = token_details.get('cache_read', 0)
        
        elif hasattr(response, 'response_metadata'):
            resp_meta = response.response_metadata
            if 'usage' in resp_meta:
                usage = resp_meta['usage']
                metadata.input_tokens = usage.get('input_tokens', 0)
                metadata.output_tokens = usage.get('output_tokens', 0)
                metadata.cached_tokens = usage.get('cache_read_input_tokens', 0)
        
        # Calculate cost
        metadata.cost_usd = cls.calculate_cost(
            metadata.model, 
            metadata.input_tokens, 
            metadata.output_tokens
        )
        
        return metadata
    
    @staticmethod
    def update_session_metadata(session_metadata: SessionMetadata, response_metadata: ResponseMetadata) -> None:
        """Update cumulative session metadata with the latest response"""
        session_metadata.total_api_calls += 1
        session_metadata.total_input_tokens += response_metadata.input_tokens
        session_metadata.total_output_tokens += response_metadata.output_tokens
        session_metadata.total_cached_tokens += response_metadata.cached_tokens
        session_metadata.total_cost_usd += response_metadata.cost_usd
        session_metadata.total_response_time_ms += response_metadata.response_time_ms
        session_metadata.last_call_time = datetime.now()
    
    @staticmethod
    def format_response_metadata(metadata: ResponseMetadata) -> str:
        """Format last response metadata for display"""
        return f"""
📊 LAST RESPONSE METADATA
{'='*40}
🤖 Model: {metadata.model}
⏱️  Response Time: {metadata.response_time_ms}ms
📥 Input Tokens: {metadata.input_tokens:,}
📤 Output Tokens: {metadata.output_tokens:,}
🔄 Cached Tokens: {metadata.cached_tokens:,}
💰 Cost (USD): ${metadata.cost_usd:.6f}
{'='*40}
        """
    
    @staticmethod
    def format_session_metadata(session_metadata: SessionMetadata) -> str:
        """Format cumulative session metadata for display"""
        if session_metadata.total_api_calls == 0:
            return "\n📊 SESSION METADATA\n" + "="*40 + "\n❌ No API calls made yet\n" + "="*40 + "\n"
        
        # Calculate session duration
        session_duration = datetime.now() - session_metadata.session_start_time
        session_duration_str = str(session_duration).split('.')[0]  # Remove microseconds
        
        # Calculate averages
        avg_cost_per_call = session_metadata.total_cost_usd / session_metadata.total_api_calls
        avg_response_time = session_metadata.total_response_time_ms / session_metadata.total_api_calls
        total_tokens = session_metadata.total_input_tokens + session_metadata.total_output_tokens
        
        return f"""
📊 SESSION METADATA SUMMARY
{'='*50}
🕒 Session Duration: {session_duration_str}
📞 Total API Calls: {session_metadata.total_api_calls}
📥 Total Input Tokens: {session_metadata.total_input_tokens:,}
📤 Total Output Tokens: {session_metadata.total_output_tokens:,}
🔄 Total Cached Tokens: {session_metadata.total_cached_tokens:,}
📊 Total Tokens Used: {total_tokens:,}
💰 Total Cost (USD): ${session_metadata.total_cost_usd:.6f}
⏱️  Total Response Time: {session_metadata.total_response_time_ms:,}ms

📈 AVERAGES
{'='*50}
💰 Average Cost per Call: ${avg_cost_per_call:.6f}
⏱️  Average Response Time: {avg_response_time:.0f}ms
📊 Average Tokens per Call: {total_tokens/session_metadata.total_api_calls:.0f}

📅 TIMING
{'='*50}
🏁 Session Started: {session_metadata.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}
🏃 Last API Call: {session_metadata.last_call_time.strftime('%Y-%m-%d %H:%M:%S') if session_metadata.last_call_time else 'None'}
{'='*50}
        """
