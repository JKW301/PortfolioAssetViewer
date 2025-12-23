#!/bin/bash
set -e

echo "🔨 Building Portfolio Tracker for Render..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Build frontend POUR DE VRAI
echo "🎨 Building React frontend..."
cd frontend

# Clean install avec legacy peer deps
rm -rf node_modules build
npm install --legacy-peer-deps --force

# Build production
REACT_APP_BACKEND_URL=https://portfolio-tracker-ejlw.onrender.com npm run build

cd ..

echo "✅ Build complete!"
echo "📁 Frontend build:"
ls -la frontend/build/
du -sh frontend/build/
