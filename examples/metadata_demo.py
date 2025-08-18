#!/usr/bin/env python3
"""
Metadata Demo - Demonstrates response metadata and cost tracking features
"""

from invoice_agent import InvoiceAgent

def metadata_demo():
    """
    Demonstration of metadata tracking features
    """
    print("🤖 Invoice Agent - Metadata & Cost Tracking Demo")
    print("=" * 60)
    
    # Initialize agent
    agent = InvoiceAgent()
    
    print("\n1. Processing user input with automatic metadata display:")
    print("-" * 50)
    
    # Example 1: Partial information
    user_input = "I need an invoice for $500"
    print(f"User: {user_input}")
    response = agent.process_user_input(user_input)
    print(f"Agent: {response}")
    
    print("\n2. Accessing metadata programmatically:")
    print("-" * 50)
    
    # Get metadata object
    metadata = agent.get_last_response_metadata()
    
    print(f"🤖 Model Used: {metadata.model}")
    print(f"⏱️  Response Time: {metadata.response_time_ms}ms")
    print(f"📥 Input Tokens: {metadata.input_tokens:,}")
    print(f"📤 Output Tokens: {metadata.output_tokens:,}")
    print(f"🔄 Cached Tokens: {metadata.cached_tokens:,}")
    print(f"💰 Cost (USD): ${metadata.cost_usd:.6f}")
    print(f"📊 Total Tokens: {metadata.input_tokens + metadata.output_tokens:,}")
    
    if metadata.cost_usd > 0:
        cost_per_token = metadata.cost_usd / (metadata.input_tokens + metadata.output_tokens)
        print(f"💱 Cost per Token: ${cost_per_token:.8f}")
    
    print("\n3. Continuing conversation and tracking cumulative costs:")
    print("-" * 50)
    
    # Track cumulative costs
    cumulative_cost = metadata.cost_usd
    cumulative_tokens = metadata.input_tokens + metadata.output_tokens
    
    # Continue conversation
    user_input2 = "Customer is John Smith, email john@email.com, consulting services, due 2025-01-15"
    print(f"User: {user_input2}")
    response2 = agent.process_user_input(user_input2)
    
    # Get metadata for second call
    metadata2 = agent.get_last_response_metadata()
    cumulative_cost += metadata2.cost_usd
    cumulative_tokens += metadata2.input_tokens + metadata2.output_tokens
    
    print(f"Agent: {response2}")
    
    print("\n4. Cumulative Session Statistics:")
    print("-" * 50)
    print(f"💰 Total Session Cost: ${cumulative_cost:.6f}")
    print(f"📊 Total Session Tokens: {cumulative_tokens:,}")
    print(f"🔄 Number of API Calls: 2")
    print(f"💱 Average Cost per Call: ${cumulative_cost/2:.6f}")
    
    print("\n5. Cost Estimation for Different Models:")
    print("-" * 50)
    
    # Show cost comparison for different models
    sample_tokens = {"input": 1000, "output": 500}
    
    for model, pricing in agent.pricing.items():
        cost = agent.calculate_cost(model, sample_tokens["input"], sample_tokens["output"])
        print(f"{model}: ${cost:.6f} (for 1K input + 500 output tokens)")
    
    print("\n6. Formatted Metadata Display:")
    print("-" * 50)
    formatted = agent.get_formatted_metadata()
    print(formatted)

def cost_monitoring_example():
    """
    Example of how to monitor costs in a production application
    """
    print("\n" + "=" * 60)
    print("🏭 PRODUCTION COST MONITORING EXAMPLE")
    print("=" * 60)
    
    agent = InvoiceAgent()
    
    # Simulate a session with multiple interactions
    session_cost = 0.0
    session_tokens = 0
    call_count = 0
    
    test_inputs = [
        "Create invoice for $1200",
        "Customer is Sarah Wilson, email sarah@company.com",
        "Description is web development services",
        "Due date is 2025-02-15",
        "APPROVE"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\nCall {i}: {user_input}")
        response = agent.process_user_input(user_input)
        
        # Track costs (in production, you'd log this to a database)
        metadata = agent.get_last_response_metadata()
        session_cost += metadata.cost_usd
        session_tokens += metadata.input_tokens + metadata.output_tokens
        call_count += 1
        
        print(f"Call {i} cost: ${metadata.cost_usd:.6f}")
        
        # Cost alerts (example thresholds)
        if metadata.cost_usd > 0.01:  # Alert if single call > 1 cent
            print(f"⚠️  HIGH COST ALERT: Call cost ${metadata.cost_usd:.6f}")
        
        if session_cost > 0.05:  # Alert if session > 5 cents
            print(f"⚠️  SESSION COST ALERT: Total ${session_cost:.6f}")
    
    print(f"\n📊 FINAL SESSION REPORT:")
    print(f"Total Cost: ${session_cost:.6f}")
    print(f"Total Tokens: {session_tokens:,}")
    print(f"Total API Calls: {call_count}")
    print(f"Average Cost per Call: ${session_cost/call_count:.6f}")
    print(f"Cost per Token: ${session_cost/session_tokens:.8f}")

if __name__ == "__main__":
    try:
        metadata_demo()
        cost_monitoring_example()
    except Exception as e:
        print(f"Demo error: {e}")
        print("Make sure you have set your ANTHROPIC_API_KEY in the .env file")
