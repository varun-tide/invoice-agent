"""
Backward Compatibility Layer
Maintains the original interface while using the new refactored components
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    # Import everything from the new structure for backward compatibility
    from agent import InvoiceAgent
    from domain.models import InvoiceData, ResponseMetadata, SessionMetadata
    from cli import demo_invoice_agent
except ImportError:
    # Fallback for when running from different contexts
    sys.path.insert(0, str(current_dir.parent))
    from agent.agent import InvoiceAgent
    from agent.domain.models import InvoiceData, ResponseMetadata, SessionMetadata
    from agent.cli import demo_invoice_agent

# Export the same interface as before
__all__ = [
    "InvoiceAgent",
    "InvoiceData", 
    "ResponseMetadata",
    "SessionMetadata",
    "demo_invoice_agent"
]

# Main execution for backward compatibility
if __name__ == "__main__":
    demo_invoice_agent()
