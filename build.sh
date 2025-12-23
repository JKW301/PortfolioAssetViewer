#!/bin/bash
set -e

echo "🔨 Building Portfolio Tracker for Render..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Build frontend
echo "🎨 Building React frontend..."
cd frontend
npm install --legacy-peer-deps
npm run build
cd ..

echo "✅ Build complete!"
echo "📁 Frontend build size:"
du -sh frontend/build/
