#!/bin/bash
set -e

echo "🔨 Installing Python dependencies..."
pip install -r requirements.txt

echo "� Running database migration..."
cd backend
python migrate_add_password.py || echo "⚠️  Migration already applied or not needed"
cd ..

echo "�🔨 Installing frontend dependencies..."
cd frontend
npm install --legacy-peer-deps

echo "🔨 Building React frontend..."
npm run build

echo "✅ Build complete!"
