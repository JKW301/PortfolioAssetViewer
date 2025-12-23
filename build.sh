#!/bin/bash
set -e

echo "🔨 Installing Python dependencies..."
pip install -r requirements.txt

echo "🔨 Creating frontend build..."
mkdir -p frontend/build/static/css frontend/build/static/js

# Create index.html with React Router and functional components
cat > frontend/build/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Portfolio Tracker</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/react-router-dom@6/dist/index.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .loading { animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useEffect } = React;
        const { BrowserRouter, Routes, Route, Link } = ReactRouterDOM;
        const API_BASE = window.location.origin + '/api';

        function Login() {
            const [loading, setLoading] = useState(false);
            const handleLogin = () => {
                setLoading(true);
                window.location.href = `${API_BASE}/auth/login`;
            };

            return (
                <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
                    <div className="bg-white rounded-xl shadow-xl p-8 max-w-md w-full">
                        <div className="text-center mb-8">
                            <h1 className="text-3xl font-bold text-gray-800 mb-2">Portfolio Tracker</h1>
                            <p className="text-gray-600">Track your investments in real-time</p>
                        </div>
                        <button onClick={handleLogin} disabled={loading}
                                className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white font-medium py-3 px-6 rounded-lg transition duration-200">
                            {loading ? 'Connecting...' : 'Login with Google'}
                        </button>
                        <div className="mt-6 text-center">
                            <a href="/api/docs" className="text-blue-500 hover:text-blue-600 text-sm">📚 API Documentation</a>
                        </div>
                    </div>
                </div>
            );
        }

        function Dashboard() {
            const [user, setUser] = useState(null);
            const [loading, setLoading] = useState(true);

            useEffect(() => {
                fetch(`${API_BASE}/auth/me`, { credentials: 'include' })
                    .then(r => r.ok ? r.json() : Promise.reject())
                    .then(setUser)
                    .catch(() => window.location.href = '/login')
                    .finally(() => setLoading(false));
            }, []);

            const handleLogout = () => {
                fetch(`${API_BASE}/auth/logout`, { method: 'POST', credentials: 'include' })
                    .then(() => window.location.href = '/login');
            };

            if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="loading w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div></div>;

            return (
                <div className="min-h-screen bg-gray-50">
                    <header className="bg-white shadow-sm border-b">
                        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div className="flex justify-between items-center h-16">
                                <h1 className="text-xl font-bold text-gray-900">Portfolio Tracker</h1>
                                <div className="flex items-center gap-4">
                                    <Link to="/history" className="text-gray-600 hover:text-gray-900">History</Link>
                                    <span className="text-sm text-gray-600">Welcome, {user?.name || 'User'}!</span>
                                    <button onClick={handleLogout} className="text-red-600 hover:text-red-700 text-sm">Logout</button>
                                </div>
                            </div>
                        </div>
                    </header>
                    <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                            <div className="bg-white shadow rounded-lg p-5">
                                <h3 className="text-sm font-medium text-gray-500">Total Portfolio</h3>
                                <p className="text-lg font-medium text-gray-900">€0.00</p>
                            </div>
                            <div className="bg-white shadow rounded-lg p-5">
                                <h3 className="text-sm font-medium text-gray-500">Crypto Assets</h3>
                                <p className="text-lg font-medium text-gray-900">0</p>
                            </div>
                            <div className="bg-white shadow rounded-lg p-5">
                                <h3 className="text-sm font-medium text-gray-500">Stock Assets</h3>
                                <p className="text-lg font-medium text-gray-900">0</p>
                            </div>
                        </div>
                        <div className="bg-white shadow rounded-lg p-6">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">Getting Started</h3>
                            <p className="text-gray-600 mb-4">Welcome to Portfolio Tracker! Add assets using the API.</p>
                            <a href="/api/docs" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200">📚 API Documentation</a>
                        </div>
                    </main>
                </div>
            );
        }

        function History() {
            return (
                <div className="min-h-screen bg-gray-50">
                    <header className="bg-white shadow-sm border-b">
                        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div className="flex items-center h-16">
                                <Link to="/dashboard" className="text-blue-500 hover:text-blue-600 mr-4">← Back</Link>
                                <h1 className="text-xl font-bold text-gray-900">Portfolio History</h1>
                            </div>
                        </div>
                    </header>
                    <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                        <div className="bg-white shadow rounded-lg p-6 text-center">
                            <h2 className="text-lg font-semibold text-gray-900 mb-4">Historical Performance</h2>
                            <p className="text-gray-500">No historical data available yet.</p>
                        </div>
                    </main>
                </div>
            );
        }

        function App() {
            return (
                <BrowserRouter>
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/history" element={<History />} />
                        <Route path="/" element={<Dashboard />} />
                    </Routes>
                </BrowserRouter>
            );
        }

        ReactDOM.render(<App />, document.getElementById('root'));
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
