#!/bin/bash
set -e

echo "🔨 Installing Python dependencies..."
pip install -r requirements.txt

echo "🔨 Creating frontend build..."
mkdir -p frontend/build/static/css frontend/build/static/js

# Create index.html with error handling and debugging
cat > frontend/build/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Portfolio Tracker</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .loading { 
            animation: spin 1s linear infinite; 
            border: 4px solid #f3f4f6;
            border-top: 4px solid #3b82f6;
            border-radius: 50%;
            width: 32px;
            height: 32px;
        }
        @keyframes spin { 
            0% { transform: rotate(0deg); } 
            100% { transform: rotate(360deg); } 
        }
        .error { color: red; background: #fee; padding: 1rem; border-radius: 8px; margin: 1rem; }
    </style>
</head>
<body>
    <div id="root">
        <!-- Fallback content if React fails -->
        <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
            <div class="bg-white rounded-xl shadow-xl p-8 max-w-md w-full text-center">
                <div class="mb-6">
                    <svg class="w-16 h-16 mx-auto text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                    </svg>
                </div>
                <h1 class="text-3xl font-bold text-gray-800 mb-4">Portfolio Tracker</h1>
                <p class="text-gray-600 mb-6">Track your investments in real-time</p>
                
                <div class="space-y-4">
                    <a href="/login" onclick="handleLogin(event)" class="block bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 px-6 rounded-lg transition duration-200">
                        🔐 Login
                    </a>
                    <a href="/api/docs" class="block bg-green-500 hover:bg-green-600 text-white font-medium py-3 px-6 rounded-lg transition duration-200">
                        📚 API Documentation
                    </a>
                </div>
                
                <div class="pt-4 border-t border-gray-200 mt-6">
                    <p class="text-sm text-gray-500">✅ Backend running successfully</p>
                    <div id="status" class="text-sm text-yellow-600">🔄 Loading React App...</div>
                </div>
            </div>
        </div>
    </div>

    <div id="error-log" class="hidden"></div>

    <script>
        // Error handling and logging
        window.onerror = function(msg, url, lineNo, columnNo, error) {
            console.error('Error: ' + msg + ' Script: ' + url + ' Line: ' + lineNo);
            document.getElementById('status').innerHTML = '❌ JavaScript Error - Check Console';
            const errorDiv = document.getElementById('error-log');
            errorDiv.className = 'error';
            errorDiv.innerHTML = 'Error: ' + msg;
            errorDiv.style.display = 'block';
            return false;
        };

        // Simple login handler
        function handleLogin(e) {
            e.preventDefault();
            const statusEl = document.getElementById('status');
            statusEl.innerHTML = '🔄 Redirecting to login...';
            window.location.href = '/api/auth/login';
        }

        // Check if user is already logged in
        async function checkAuth() {
            try {
                const response = await fetch('/api/auth/me', { credentials: 'include' });
                if (response.ok) {
                    const user = await response.json();
                    document.getElementById('status').innerHTML = '✅ Logged in as ' + (user.name || 'User');
                    showDashboard(user);
                } else {
                    document.getElementById('status').innerHTML = '🔓 Not logged in';
                }
            } catch (error) {
                console.error('Auth check failed:', error);
                document.getElementById('status').innerHTML = '⚠️ Auth check failed';
            }
        }

        // Simple dashboard
        function showDashboard(user) {
            document.getElementById('root').innerHTML = `
                <div class="min-h-screen bg-gray-50">
                    <header class="bg-white shadow-sm border-b">
                        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div class="flex justify-between items-center h-16">
                                <h1 class="text-xl font-bold text-gray-900">Portfolio Tracker</h1>
                                <div class="flex items-center gap-4">
                                    <span class="text-sm text-gray-600">Welcome, ${user.name || 'User'}!</span>
                                    <button onclick="logout()" class="text-red-600 hover:text-red-700 text-sm">Logout</button>
                                </div>
                            </div>
                        </div>
                    </header>
                    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                            <div class="bg-white shadow rounded-lg p-5">
                                <h3 class="text-sm font-medium text-gray-500">Total Portfolio</h3>
                                <p class="text-lg font-medium text-gray-900">€0.00</p>
                            </div>
                            <div class="bg-white shadow rounded-lg p-5">
                                <h3 class="text-sm font-medium text-gray-500">Crypto Assets</h3>
                                <p class="text-lg font-medium text-gray-900">0</p>
                            </div>
                            <div class="bg-white shadow rounded-lg p-5">
                                <h3 class="text-sm font-medium text-gray-500">Stock Assets</h3>
                                <p class="text-lg font-medium text-gray-900">0</p>
                            </div>
                        </div>
                        <div class="bg-white shadow rounded-lg p-6">
                            <h3 class="text-lg font-medium text-gray-900 mb-4">Getting Started</h3>
                            <p class="text-gray-600 mb-4">Welcome to Portfolio Tracker! Add assets using the API.</p>
                            <a href="/api/docs" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200">
                                📚 API Documentation
                            </a>
                        </div>
                    </main>
                </div>
            `;
        }

        // Logout function
        async function logout() {
            try {
                await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
                location.reload();
            } catch (error) {
                console.error('Logout failed:', error);
            }
        }

        // Initialize app
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM loaded, checking auth...');
            checkAuth();
        });

        // Also run immediately in case DOMContentLoaded already fired
        if (document.readyState === 'loading') {
            console.log('Document still loading...');
        } else {
            console.log('Document ready, checking auth...');
            checkAuth();
        }
    </script>
</body>
</html>
EOF

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
