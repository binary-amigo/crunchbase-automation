#!/usr/bin/env bash
# Build script for Render deployment

echo "🚀 Starting build process..."

# Upgrade pip and setuptools
echo "📦 Upgrading build tools..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p logs

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 uploads
chmod 755 logs

echo "✅ Build completed successfully!" 