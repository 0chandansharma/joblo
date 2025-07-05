#!/bin/bash

echo "Setting up JobLo Assistant..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your OpenAI API key"
fi

# Create data directories
mkdir -p data/raw data/processed

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Start MongoDB: mongod"
echo "3. Run the demo: python demo.py"
echo "4. Or try the CLI: python main.py chat"