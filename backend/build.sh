#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Starting build process..."

# Check Python version
echo "Python version:"
python --version

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv .venv
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements-render.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p logs

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 uploads
chmod 755 logs

echo "✅ Build completed successfully!" 