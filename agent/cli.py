"""
Command Line Interface - Terminal interaction
Single Responsibility: Handle CLI interaction
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
    from agent import InvoiceAgent
except ImportError:
    # Fallback for when running from different contexts
    sys.path.insert(0, str(current_dir.parent))
    from agent.agent import InvoiceAgent


def demo_invoice_agent():
    """
    Demonstration of the Invoice Agent via command line
    """
    print("🤖 Invoice Agent Demo")
    print("=" * 50)
    
    # Initialize agent (API key from environment)
    agent = InvoiceAgent()
    
    print("Agent: Hello! I'm your Invoice Agent. I'll help you create an invoice.")
    print("Agent: Please provide the invoice details - customer name, email, description, amount, and due date.")
    print("\nType 'quit' to exit the demo.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! Thanks for using the Invoice Agent.")
            break
        
        if user_input:
            response = agent.process_user_input(user_input)
            print(f"Agent: {response}\n")


if __name__ == "__main__":
    demo_invoice_agent()
