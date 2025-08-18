"""
Infrastructure - Invoice Agent Service Implementation
Following Clean Architecture: Infrastructure layer (outermost)
"""

import sys
from pathlib import Path
from typing import Optional

# Add agent directory to path to import the invoice agent
project_root = Path(__file__).parent.parent.parent
agent_path = project_root / "agent"
if agent_path.exists():
    sys.path.insert(0, str(agent_path))

try:
    from invoice_agent import InvoiceAgent  # type: ignore
    print("✅ Successfully imported real InvoiceAgent from agent/ directory")
except ImportError as e:
    # Fallback: create a mock agent for testing
    print(f"⚠️  Warning: Could not import InvoiceAgent ({e}), using mock implementation")
    
    class InvoiceAgent:
        def __init__(self):
            self.invoice_data = type('obj', (object,), {
                'customer_name': None,
                'customer_email': None, 
                'invoice_description': None,
                'total_amount': None,
                'due_date': None,
                'get_missing_fields': lambda: []
            })()
            self.session_metadata = type('obj', (object,), {
                'total_api_calls': 0,
                'total_cost_usd': 0.0,
                'model_dump': lambda: {}
            })()
        
        def process_user_input(self, user_input: str) -> str:
            return f"Mock response to: {user_input}"
        
        def process_user_input_api(self, user_input: str) -> dict:
            return {
                "success": True,
                "action": "text_response",
                "message": f"Mock response to: {user_input}",
                "invoice_status": "processing"
            }
        
        def get_session_metadata(self):
            return self.session_metadata

from ..application.interfaces import IInvoiceAgentService
from ..domain.entities import ConversationSession


class InvoiceAgentService(IInvoiceAgentService):
    """
    Concrete implementation of Invoice Agent Service
    Adapter pattern: Adapts existing InvoiceAgent to our interface
    """
    
    def __init__(self):
        # Map session_id to agent instance for stateful conversations
        self._agents: dict[str, InvoiceAgent] = {}
    
    async def process_user_input(
        self, 
        user_input: str, 
        session: ConversationSession
    ) -> str:
        """
        Process user input using the invoice agent
        """
        # Get or create agent for this session
        agent = self._get_agent_for_session(session.session_id)
        
        # Process input
        response = agent.process_user_input(user_input)
        
        # Update session with agent data
        await self._sync_agent_to_session(agent, session)
        
        return response
    
    async def process_user_input_api(
        self, 
        user_input: str, 
        session: ConversationSession
    ) -> dict:
        """
        Process user input using the invoice agent - API version
        Returns structured data instead of formatted strings
        """
        try:
            # Get or create agent for this session
            agent = self._get_agent_for_session(session.session_id)
            
            # Check if agent has the new API method
            if hasattr(agent, 'process_user_input_api'):
                # Use the new API-friendly method
                response = agent.process_user_input_api(user_input)
            else:
                # Fallback for older agents - convert string response to dict
                string_response = agent.process_user_input(user_input)
                response = {
                    "success": True,
                    "action": "text_response",
                    "message": string_response,
                    "invoice_status": "processing"
                }
            
            # Update session with agent data
            await self._sync_agent_to_session(agent, session)
            
            return response
            
        except Exception as e:
            error_str = str(e)
            
            # Handle specific API error cases
            if "overloaded" in error_str.lower() or "529" in error_str:
                return {
                    "success": False,
                    "action": "error",
                    "message": "The AI service is temporarily overloaded. Please try again in a few minutes.",
                    "error_type": "service_overloaded",
                    "invoice_status": "error"
                }
            elif "rate limit" in error_str.lower():
                return {
                    "success": False,
                    "action": "error", 
                    "message": "Rate limit exceeded. Please wait a moment before trying again.",
                    "error_type": "rate_limit",
                    "invoice_status": "error"
                }
            elif "authentication" in error_str.lower() or "api_key" in error_str.lower():
                return {
                    "success": False,
                    "action": "error",
                    "message": "Authentication error. Please contact support.",
                    "error_type": "authentication",
                    "invoice_status": "error"
                }
            else:
                return {
                    "success": False,
                    "action": "error",
                    "message": f"An unexpected error occurred: {error_str}",
                    "error_type": "unknown",
                    "invoice_status": "error"
                }
    
    async def get_session_metadata(self, session: ConversationSession) -> dict:
        """Get formatted session metadata"""
        agent = self._get_agent_for_session(session.session_id)
        
        # Try to get metadata from real agent first
        try:
            if hasattr(agent, 'get_session_metadata'):
                agent_metadata = agent.get_session_metadata()
                if hasattr(agent_metadata, 'model_dump'):
                    return agent_metadata.model_dump()
                else:
                    # Convert to dict if it's a plain object
                    return {
                        'total_api_calls': getattr(agent_metadata, 'total_api_calls', 0),
                        'total_input_tokens': getattr(agent_metadata, 'total_input_tokens', 0),
                        'total_output_tokens': getattr(agent_metadata, 'total_output_tokens', 0),
                        'total_cached_tokens': getattr(agent_metadata, 'total_cached_tokens', 0),
                        'total_cost_usd': getattr(agent_metadata, 'total_cost_usd', 0.0),
                        'total_response_time_ms': getattr(agent_metadata, 'total_response_time_ms', 0),
                        'session_start_time': getattr(agent_metadata, 'session_start_time', session.created_at).isoformat() if hasattr(getattr(agent_metadata, 'session_start_time', None), 'isoformat') else str(getattr(agent_metadata, 'session_start_time', session.created_at)),
                        'last_call_time': getattr(agent_metadata, 'last_call_time', None).isoformat() if getattr(agent_metadata, 'last_call_time', None) and hasattr(getattr(agent_metadata, 'last_call_time', None), 'isoformat') else str(getattr(agent_metadata, 'last_call_time', None)) if getattr(agent_metadata, 'last_call_time', None) else None
                    }
        except Exception as e:
            print(f"Warning: Could not get agent metadata: {e}")
        
        # Fallback to session metadata
        return session.metadata.model_dump()
    
    def _get_agent_for_session(self, session_id: str) -> InvoiceAgent:
        """Get or create agent instance for session"""
        if session_id not in self._agents:
            self._agents[session_id] = InvoiceAgent()
        return self._agents[session_id]
    
    async def _sync_agent_to_session(
        self, 
        agent: InvoiceAgent, 
        session: ConversationSession
    ) -> None:
        """
        Synchronize agent state with session entity
        """
        try:
            # Sync invoice data from real agent
            if hasattr(agent, 'invoice_data'):
                agent_data = agent.invoice_data
                
                # Update session invoice data from agent's InvoiceData model
                session.invoice_data.customer_name = getattr(agent_data, 'customer_name', None)
                session.invoice_data.customer_email = getattr(agent_data, 'customer_email', None)
                session.invoice_data.invoice_description = getattr(agent_data, 'invoice_description', None)
                session.invoice_data.total_amount = getattr(agent_data, 'total_amount', None)
                session.invoice_data.due_date = getattr(agent_data, 'due_date', None)
            
            # Sync metadata from real agent's session metadata
            if hasattr(agent, 'session_metadata'):
                agent_metadata = agent.session_metadata
                
                # Update session metadata from agent's SessionMetadata model
                session.metadata.total_api_calls = getattr(agent_metadata, 'total_api_calls', 0)
                session.metadata.total_input_tokens = getattr(agent_metadata, 'total_input_tokens', 0)
                session.metadata.total_output_tokens = getattr(agent_metadata, 'total_output_tokens', 0)
                session.metadata.total_cached_tokens = getattr(agent_metadata, 'total_cached_tokens', 0)
                session.metadata.total_cost_usd = getattr(agent_metadata, 'total_cost_usd', 0.0)
                session.metadata.total_response_time_ms = getattr(agent_metadata, 'total_response_time_ms', 0)
                
                # Update timestamps
                if hasattr(agent_metadata, 'last_call_time') and agent_metadata.last_call_time:
                    session.metadata.last_call_time = agent_metadata.last_call_time
                
        except Exception as e:
            # Don't fail the request if sync fails
            print(f"Warning: Could not sync agent to session: {e}")
    
    def cleanup_session(self, session_id: str) -> None:
        """Clean up agent instance for session"""
        if session_id in self._agents:
            del self._agents[session_id]
