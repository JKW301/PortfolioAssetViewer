#!/bin/bash
set -e

echo "🔨 Building Portfolio Tracker for Render..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build complete!"
echo "📁 Using pre-built frontend from /frontend/build/"
ls -la frontend/build/ || echo "Warning: frontend build not found"
