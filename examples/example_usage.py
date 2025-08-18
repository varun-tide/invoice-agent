#!/usr/bin/env python3
"""
Example usage of the Invoice Agent
This demonstrates different scenarios and use cases
"""

from invoice_agent import InvoiceAgent
import os

def test_scenario_1():
    """Scenario 1: User provides all information at once"""
    print("\n" + "="*60)
    print("SCENARIO 1: Complete information provided at once")
    print("="*60)
    
    agent = InvoiceAgent()
    
    # User provides complete information
    user_input = """
    I need to create an invoice for John Smith at john.smith@email.com.
    The invoice is for web development services totaling $2500.
    The due date should be January 15, 2025.
    """
    
    print(f"User Input: {user_input.strip()}")
    response = agent.process_user_input(user_input)
    print(f"Agent Response: {response}")
    
    # User approves
    print("\nUser: APPROVE")
    response = agent.process_user_input("APPROVE")
    print(f"Agent Response: {response}")
    
    # Show metadata access
    print(f"\nMetadata for last call: {agent.get_formatted_metadata()}")

def test_scenario_2():
    """Scenario 2: User provides partial information, agent requests missing fields"""
    print("\n" + "="*60)
    print("SCENARIO 2: Partial information, iterative collection")
    print("="*60)
    
    agent = InvoiceAgent()
    
    # Step 1: Partial information
    print("User: I need an invoice for Jane Doe for $1200")
    response = agent.process_user_input("I need an invoice for Jane Doe for $1200")
    print(f"Agent: {response}")
    
    # Step 2: Provide more info
    print("\nUser: Her email is jane.doe@company.com and it's for consulting services")
    response = agent.process_user_input("Her email is jane.doe@company.com and it's for consulting services")
    print(f"Agent: {response}")
    
    # Step 3: Provide due date
    print("\nUser: Due date should be 2025-02-01")
    response = agent.process_user_input("Due date should be 2025-02-01")
    print(f"Agent: {response}")
    
    # Step 4: Approve
    print("\nUser: APPROVE")
    response = agent.process_user_input("APPROVE")
    print(f"Agent: {response}")

def test_scenario_3():
    """Scenario 3: User provides information in natural language"""
    print("\n" + "="*60)
    print("SCENARIO 3: Natural language input")
    print("="*60)
    
    agent = InvoiceAgent()
    
    # Natural language input
    user_input = """
    Hi! I just finished a project for ABC Corp. The client contact is 
    Sarah Wilson and her email is s.wilson@abccorp.com. I provided 
    graphic design services and the total comes to fifteen hundred dollars. 
    They usually pay within 30 days, so let's set the due date for next month.
    """
    
    print(f"User: {user_input.strip()}")
    response = agent.process_user_input(user_input)
    print(f"Agent: {response}")

def test_mobile_app_integration():
    """Example of how this would integrate with a mobile app"""
    print("\n" + "="*60)
    print("MOBILE APP INTEGRATION EXAMPLE")
    print("="*60)
    
    print("""
    In a mobile app, you would:
    
    1. Initialize the agent when user starts creating an invoice:
       agent = InvoiceAgent()
    
    2. Process voice-to-text or typed input:
       response = agent.process_user_input(user_speech_or_text)
    
    3. Display the response in your chat UI
    
    4. When user approves, handle the API response:
       - Show success message
       - Display preview/download buttons
       - Navigate to invoice preview screen
    
    5. For the CTA buttons, you can use:
       - Preview: Open webview with preview_url
       - Download: Download PDF from pdf_url
       - Share: Use platform sharing with the invoice link
    """)

def interactive_demo():
    """Interactive demo for testing"""
    print("\n" + "="*60)
    print("INTERACTIVE DEMO - Test your own inputs!")
    print("="*60)
    
    agent = InvoiceAgent()
    
    print("Invoice Agent: Hello! I'll help you create an invoice.")
    print("Invoice Agent: Please provide customer details, description, amount, and due date.")
    print("\nType 'quit' to exit, 'reset' to start over.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("Invoice Agent: Goodbye!")
            break
        elif user_input.lower() == 'reset':
            agent.reset()
            print("Invoice Agent: Starting fresh! Please provide your invoice details.")
            continue
        
        if user_input:
            try:
                response = agent.process_user_input(user_input)
                print(f"Invoice Agent: {response}\n")
                
                # Optionally show metadata for each interaction
                # Uncomment the next line to see metadata for every interaction
                # print(f"Metadata: {agent.get_formatted_metadata()}")
            except Exception as e:
                print(f"Error: {e}\n")

if __name__ == "__main__":
    print("🤖 Invoice Agent Examples and Testing")
    print("Choose a demo to run:")
    print("1. Scenario 1: Complete information at once")
    print("2. Scenario 2: Iterative information collection")
    print("3. Scenario 3: Natural language processing")
    print("4. Mobile app integration info")
    print("5. Interactive demo")
    print("6. Run all scenarios")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        test_scenario_1()
    elif choice == "2":
        test_scenario_2()
    elif choice == "3":
        test_scenario_3()
    elif choice == "4":
        test_mobile_app_integration()
    elif choice == "5":
        interactive_demo()
    elif choice == "6":
        test_scenario_1()
        test_scenario_2()
        test_scenario_3()
        test_mobile_app_integration()
    else:
        print("Invalid choice. Running interactive demo...")
        interactive_demo()
