#!/usr/bin/env python3
"""
Simple script to run the Invoice Agent
This script handles imports properly and provides helpful error messages
"""

import sys
import os
from pathlib import Path

def setup_python_path():
    """Setup Python path to find the agent directory"""
    current_dir = Path(__file__).parent.absolute()
    agent_dir = current_dir / "agent"
    
    if agent_dir.exists():
        sys.path.insert(0, str(agent_dir))
        return True
    else:
        print(f"❌ Error: agent directory not found at {agent_dir}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    required_modules = [
        'langchain_anthropic',
        'dotenv', 
        'pydantic',
        'dateutil'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Missing required modules:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\n🔧 Please install requirements:")
        print("   pip install -r requirements.txt")
        return False
    return True

def main():
    """Main function to run the Invoice Agent"""
    print("🚀 Starting Invoice Agent...")
    
    # Setup Python path
    if not setup_python_path():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        
        # Load .env from project root (standard location)
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Loaded environment from {env_path}")
        else:
            load_dotenv()  # Try default locations
        
        # Check for Anthropic API key
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            print("⚠️  Warning: ANTHROPIC_API_KEY not found in environment variables")
            print("   Please create a .env file in the project root with your API key:")
            print("   echo 'ANTHROPIC_API_KEY=your_key_here' > .env")
            print("   Continuing anyway (agent may not work properly)...\n")
        else:
            print("✅ API key found and loaded")
            
    except Exception as e:
        print(f"❌ Error loading environment: {e}")
        sys.exit(1)
    
    # Import and run the agent
    try:
        from invoice_agent import InvoiceAgent
        print("✅ Invoice Agent loaded successfully!")
        print()
        
        # Run interactive agent
        interactive_agent()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("🔧 Try running: pip install -e .")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def interactive_agent():
    """Interactive Invoice Agent CLI"""
    from invoice_agent import InvoiceAgent
    
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
    main()
