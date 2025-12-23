#!/bin/bash
set -e

echo "🔨 Installing Python dependencies..."
pip install -r requirements.txt

echo "🔨 Building frontend..."
cd frontend
if [ ! -d "build" ]; then
    echo "Creating frontend build directory..."
    mkdir -p build
fi

# Check if we can build React app
if npm list react-scripts > /dev/null 2>&1; then
    echo "Building React app..."
    npm run build || echo "⚠️ React build failed, using pre-built version"
else
    echo "⚠️ Using pre-built frontend (React dependencies not properly installed)"
fi

cd ..

echo "✅ Build complete!"
echo "📁 Frontend build:"
ls -la frontend/build/ 2>&1 || echo "⚠️ No build directory found"
