#!/bin/bash
set -e

echo "🔨 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build complete!"
echo "📁 Frontend build (pre-built locally):"
ls -la frontend/build/ 2>&1 || echo "⚠️ Frontend build missing - upload frontend/build/ to Git"
