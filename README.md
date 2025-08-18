# Invoice Agent Tool

An intelligent invoice creation agent powered by Anthropic's Claude API that collects, validates, and processes invoice information through natural language conversation.

## Features

- 🤖 **Natural Language Processing**: Understands invoice details from conversational input
- ✅ **Smart Validation**: Validates email formats, amounts, and date formats
- 🔄 **Iterative Collection**: Requests missing information intelligently
- 📋 **Preview & Approval**: Shows formatted preview before creation
- 🔗 **API Integration**: Simulates invoice creation with preview links
- 📱 **Mobile-Ready**: Designed for mobile app integration

## Required Fields

The agent collects and validates these required fields:

1. **Customer Name** - Full name of the customer
2. **Customer Email** - Valid email address
3. **Invoice Description** - Description of services/products
4. **Total Amount** - Amount in dollars (must be > 0)
5. **Due Date** - Flexible date format (see Natural Date Processing below)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables:
```bash
# Create .env file with your Anthropic API key
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

## Quick Start

### Basic Usage

```python
from invoice_agent import InvoiceAgent

# Initialize the agent
agent = InvoiceAgent()

# Process user input
response = agent.process_user_input(
    "Create invoice for John Doe at john@email.com for $500 web development, due 2024-12-31"
)
print(response)

# If all info is provided, user can approve
approval_response = agent.process_user_input("APPROVE")
print(approval_response)
```

### Interactive Demo

Run the example script:
```bash
python example_usage.py
```

## Step-by-Step Guide

### Step 1: Initialize the Agent
```python
from invoice_agent import InvoiceAgent
agent = InvoiceAgent()
```

### Step 2: Process User Input
The agent can handle various input formats:
- **Complete**: "Invoice for Sarah at sarah@email.com, $1200 for consulting, due 2024-12-15"
- **Partial**: "Need invoice for $800"
- **Natural**: "I just finished work for ABC Corp, contact is Mike Johnson..."

### Step 3: Handle Missing Information
The agent will automatically request missing fields:
```python
response = agent.process_user_input("Invoice for $500")
# Agent will ask for customer name, email, description, and due date
```

### Step 4: Preview and Approval
When all fields are collected, the agent shows a preview:
```
📧 INVOICE PREVIEW 📧

👤 Customer Information:
Name: John Doe
Email: john@email.com

📝 Invoice Details:
Description: Web development services
Amount: $500.00
Due Date: 2024-12-31

Reply with "APPROVE" to create the invoice...
```

### Step 5: Invoice Creation
After approval, the agent creates the invoice and provides action links:
```
✅ Invoice Created Successfully!

Invoice ID: INV-20241215-1234
Status: Created

🔗 Actions Available:
📄 Preview Invoice: https://your-app.com/invoice/INV-20241215-1234/preview
📥 Download PDF: https://your-app.com/invoice/INV-20241215-1234/pdf
```

## Mobile App Integration

### For React Native / Flutter / Native Apps:

1. **Initialize Agent**: Create agent instance when user starts invoice creation
2. **Process Input**: Send user speech-to-text or typed input to `process_user_input()`
3. **Display Response**: Show agent response in chat UI
4. **Handle CTAs**: Use the returned URLs for preview/download buttons

Example integration:
```python
# In your mobile app backend/API
def create_invoice_conversation(user_input):
    agent = InvoiceAgent()
    response = agent.process_user_input(user_input)
    
    return {
        "message": response,
        "status": "collecting" if agent.get_missing_fields() else "ready_for_approval"
    }
```

## Advanced Features

### Response Metadata and Cost Tracking

The agent automatically tracks and displays metadata for each API call:

```python
# Process user input (metadata is automatically included)
response = agent.process_user_input("Create invoice for John Doe...")
print(response)  # Includes metadata at the bottom

# Access metadata separately
metadata = agent.get_last_response_metadata()
print(f"Model: {metadata.model}")
print(f"Input tokens: {metadata.input_tokens}")
print(f"Output tokens: {metadata.output_tokens}")
print(f"Cached tokens: {metadata.cached_tokens}")
print(f"Cost: ${metadata.cost_usd:.6f}")
print(f"Response time: {metadata.response_time_ms}ms")

# Get formatted metadata string
formatted_metadata = agent.get_formatted_metadata()
print(formatted_metadata)
```

**Metadata Includes:**
- 🤖 Model used (e.g., claude-opus-4-1-20250805)
- ⏱️ Response time in milliseconds
- 📥 Input tokens count
- 📤 Output tokens count  
- 🔄 Cached tokens count
- 💰 Cost in USD (calculated based on current pricing)

**Cost Calculation:**
The agent includes pricing for major Claude models:
- **Claude Opus**: $15/1M input tokens, $75/1M output tokens
- **Claude Sonnet**: $3/1M input tokens, $15/1M output tokens
- **Claude Haiku**: $0.25/1M input tokens, $1.25/1M output tokens

### Natural Date Processing

The agent now supports flexible date input formats! Users can specify due dates naturally:

**Relative Dates:**
- "30 days" or "in 30 days"
- "2 weeks" or "in 2 weeks" 
- "1 month" or "in 1 month"
- "next week", "next month"
- "tomorrow"

**Payment Terms:**
- "net 30", "net 15", "net 45"

**Absolute Dates:**
- "April 12, 2025"
- "12th April 2025" 
- "Jan 5th 2025"
- "December 31st"
- "March 15" (assumes current/next year)
- "2025-04-12"
- "12/04/2025"

```python
# Examples of natural date input:
"Due in 30 days"           → 2025-01-14
"April 12th"               → 2025-04-12
"net 30"                   → 2025-01-14
"next week"                → 2025-01-22
```

### Enhanced Description Formatting

The agent automatically formats invoice descriptions with professional numbering when multiple items are detected:

**Input Formats Supported:**
- Comma-separated: "Web development, Logo design, Content creation"
- Semicolon-separated: "Frontend development; Backend API; Database setup"
- Line breaks: "Mobile app\nUI/UX design\nDeployment"
- Bullet points: "• Website redesign\n• SEO optimization\n• Social media"
- Mixed formats: "Web development, API integration; Testing"

**Automatic Processing:**
```python
# Input:
"Web development, Logo design, Content creation"

# Automatically formatted as:
1. Web development
2. Logo design  
3. Content creation
```

**Smart Features:**
- Removes existing numbering to avoid duplication
- Handles various separators (commas, semicolons, bullets, dashes)
- Maintains single-item descriptions unchanged
- Professional numbering (1., 2., 3., etc.)

### Custom Validation
```python
# The agent automatically validates:
# - Email format (regex validation)
# - Amount > 0
# - Date parsing and conversion to YYYY-MM-DD
# - Description formatting with auto-numbering
# - Required field presence
```

### Conversation History
```python
# Access conversation history
print(agent.conversation_history)
```

### Reset for New Invoice
```python
# Start fresh for a new invoice
agent.reset()  # Also resets metadata
```

## API Reference

### InvoiceAgent Class

#### Methods:
- `process_user_input(text)`: Main method to process user input
- `get_missing_fields()`: Returns list of missing required fields
- `generate_preview()`: Creates formatted invoice preview
- `get_last_response_metadata()`: Returns ResponseMetadata object for last API call
- `get_formatted_metadata()`: Returns formatted metadata string
- `reset()`: Resets agent for new invoice

#### Properties:
- `invoice_data`: Current invoice data (InvoiceData model)
- `conversation_history`: List of conversation exchanges
- `last_response_metadata`: ResponseMetadata object with token usage and cost info

## Useful Resources

### Anthropic Documentation
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude API Guide](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [LangChain Anthropic Integration](https://python.langchain.com/docs/integrations/chat/anthropic/)

### Video Resources
- [Building AI Agents with Claude](https://www.youtube.com/results?search_query=anthropic+claude+api+tutorial)
- [LangChain Tutorial Playlist](https://www.youtube.com/results?search_query=langchain+tutorial+python)
- [Pydantic Data Validation](https://www.youtube.com/results?search_query=pydantic+python+tutorial)

### Additional Documentation
- [Pydantic Models](https://docs.pydantic.dev/latest/)
- [Python dotenv](https://pypi.org/project/python-dotenv/)
- [Regular Expressions for Email Validation](https://emailregex.com/)

## Example Workflows

### Workflow 1: Complete Information
```
User: "Invoice for ABC Corp, contact Sarah at sarah@abc.com, $2500 for web development, due 2024-12-31"
Agent: [Shows preview]
User: "APPROVE"
Agent: [Creates invoice with CTA links]
```

### Workflow 2: Iterative Collection
```
User: "Need an invoice for $1200"
Agent: "I need the customer name and email address..."
User: "Customer is John Smith, email john@email.com"
Agent: "I need the description of services..."
User: "Consulting services"
Agent: "I need the due date..."
User: "2025-01-15"
Agent: [Shows preview]
```

## Error Handling

The agent handles common errors gracefully:
- Invalid email formats
- Negative amounts
- Invalid date formats
- Missing required information

## License

This project is for educational/demonstration purposes. Make sure to handle API keys securely in production.
