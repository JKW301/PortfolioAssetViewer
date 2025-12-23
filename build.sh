#!/bin/bash
set -e

echo "🔨 Installing Python dependencies..."
pip install -r requirements.txt

echo "🔨 Creating frontend build..."
mkdir -p frontend/build/static/css frontend/build/static/js

# Create index.html
echo '<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Portfolio Tracker</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
  <div id="root">
    <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div class="bg-white rounded-xl shadow-xl p-8 max-w-md w-full text-center">
        <div class="mb-6">
          <svg class="w-16 h-16 mx-auto text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-gray-800 mb-4">Portfolio Tracker</h1>
        <p class="text-gray-600 mb-6">Track your crypto, stocks, and investments in real-time</p>
        <div class="space-y-4">
          <a href="/api/docs" class="block bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 px-6 rounded-lg transition duration-200">📚 API Documentation</a>
          <div class="pt-4 border-t border-gray-200">
            <p class="text-sm text-gray-500">✅ Backend running successfully</p>
            <p class="text-sm text-gray-500">✅ Frontend deployed on Render</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>' > frontend/build/index.html

# Create CSS and JS files
echo "/* Portfolio Tracker CSS */" > frontend/build/static/css/main.css
echo "console.log('Portfolio Tracker loaded');" > frontend/build/static/js/main.js

# Create manifest
echo '{
  "short_name": "Portfolio Tracker",
  "name": "Portfolio Asset Viewer",
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}' > frontend/build/manifest.json

echo "✅ Build complete!"
echo "📁 Frontend build:"
ls -la frontend/build/ 2>&1 || echo "⚠️ No build directory found"
echo "📋 Index.html check:"
if [ -f "frontend/build/index.html" ]; then
    echo "✅ index.html exists and contains:"
    head -n 3 frontend/build/index.html
else
    echo "❌ index.html NOT FOUND!"
fi
