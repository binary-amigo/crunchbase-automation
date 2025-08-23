#!/bin/bash

echo "Setting up CSV Upload & Google Sheets Backend..."
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "Please create a .env file with your Google Sheets configuration."
    echo "You can copy env.example to .env and fill in your values:"
    echo "  cp env.example .env"
    echo ""
    echo "Required configuration:"
    echo "  - GOOGLE_SHEET_ID: Your Google Sheet ID"
    echo "  - GOOGLE_SHEETS_CREDENTIALS_FILE: credentials.json"
    echo ""
    echo "See setup_guide.md for detailed setup instructions."
    echo ""
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if credentials.json exists
if [ ! -f "credentials.json" ]; then
    echo ""
    echo "⚠️  credentials.json not found!"
    echo "Please download your Google Sheets API credentials from Google Cloud Console"
    echo "and save them as 'credentials.json' in this directory."
    echo ""
    echo "See setup_guide.md for detailed setup instructions."
    echo ""
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Starting Flask backend..."
echo "Backend will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py 