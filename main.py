#!/usr/bin/env python3
"""
Main entry point for the Invoice Agent interactive CLI
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path for local development
project_root = Path(__file__).parent
agent_path = project_root / "agent"
sys.path.insert(0, str(agent_path))

try:
    from invoice_agent import InvoiceAgent
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("🔧 Please make sure you've installed the requirements:")
    print("   pip install -r requirements.txt")
    print("   or pip install -e .")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Interactive Invoice Agent
def interactive_agent():
    print("🤖 Interactive Invoice Agent")
    print("=" * 50)
    print("I'll help you create an invoice! Please provide the details.")
    print("Required: Customer name, email, description, amount, and due date")
    print("Type 'quit' to exit, 'reset' to start over, 'metadata' to see session summary, 'help' for all commands")
    print("=" * 50)
    
    # Initialize agent
    agent = InvoiceAgent()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Agent: Thank you for using the Invoice Agent! Goodbye! 👋")
                break
            elif user_input.lower() == 'reset':
                agent.reset()
                print("Agent: Starting fresh! Please provide your invoice details.")
                print("(Session metadata preserved - use 'reset-session' to clear all data)")
                continue
            elif user_input.lower() == 'reset-session':
                agent.reset_session()
                print("Agent: Complete session reset! All data and metadata cleared.")
                continue
            elif user_input.lower() == 'metadata':
                session_meta = agent.get_session_metadata()
                if session_meta.total_api_calls > 0:
                    print("Agent: Here's your complete session metadata:")
                    print(agent.get_formatted_session_metadata())
                else:
                    print("Agent: No API calls made yet. Make a request first!")
                continue
            elif user_input.lower() == 'help':
                print("Agent: Available commands:")
                print("- Type your invoice details naturally")
                print("- 'APPROVE' to create the invoice after preview")
                print("- 'EDIT [field]' to modify a specific field")
                print("- 'reset' to start new invoice (keeps session stats)")
                print("- 'reset-session' to clear everything including session stats")
                print("- 'metadata' to see complete session API usage summary")
                print("- 'quit' to exit")
                continue
            
            if not user_input:
                print("Agent: Please provide some information about your invoice.")
                continue
            
            # Process user input
            response = agent.process_user_input(user_input)
            print(f"Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n\nAgent: Goodbye! 👋")
            break
        except Exception as e:
            print(f"Agent: Sorry, I encountered an error: {e}")
            print("Please try again or type 'reset' to start over.")

if __name__ == "__main__":
    interactive_agent()