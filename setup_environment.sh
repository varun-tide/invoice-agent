#!/bin/bash

# Invoice Agent Environment Setup Script

echo "🚀 Setting up Invoice Agent Environment..."
echo "=" * 50

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the project root."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Install package in development mode
echo "🔗 Installing Invoice Agent in development mode..."
pip install -e .

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file template..."
    echo "ANTHROPIC_API_KEY=your_anthropic_api_key_here" > .env
    echo "⚠️  Please edit .env file and add your Anthropic API key"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 To run the Invoice Agent:"
echo "   1. Activate environment: source venv/bin/activate"
echo "   2. Add your API key to .env file"
echo "   3. Run: python run_agent.py"
echo ""
echo "🔧 Alternative quick start:"
echo "   python3 run_agent.py"
echo ""
