#!/bin/bash

echo "🎨 Setting up Frontend"
echo "====================="
echo ""

cd "$(dirname "$0")/frontend"

# Check Node version
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Found Node.js $NODE_VERSION"
else
    echo "❌ Node.js not found!"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check npm version
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ Found npm $NPM_VERSION"
else
    echo "❌ npm not found!"
    exit 1
fi

echo ""
echo "📦 Installing frontend dependencies..."
npm install

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "To run the development server:"
echo "  cd stock-ai/frontend"
echo "  npm run dev"
echo ""
