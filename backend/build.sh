#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python 3.11 explicitly
echo "Installing Python 3.11..."
pyenv install 3.11.9 -s
pyenv global 3.11.9
python --version

# Create virtual environment with Python 3.11
echo "Creating virtual environment..."
python -m venv .venv
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements-render.txt

# Clean up
echo "Build completed successfully!" 