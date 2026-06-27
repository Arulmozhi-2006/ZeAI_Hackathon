#!/usr/bin/env bash
set -e

echo "================================"
echo "AI Prompt Firewall - Frontend Setup"
echo "================================"
echo ""

# Check Node.js
echo "Checking Node.js version..."

if ! command -v node >/dev/null 2>&1; then
    echo "Error: Node.js is not installed."
    echo "Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

NODE_VERSION=$(node -v)
echo "✓ Node $NODE_VERSION found"
echo ""

# Check npm
if ! command -v npm >/dev/null 2>&1; then
    echo "Error: npm is not installed."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
echo "This may take a minute..."
npm install
echo "✓ Dependencies installed"
echo ""

# Create .env.local safely (cross-platform check)
echo "Setting up environment file..."

if [ ! -f ".env.local" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env.local
        echo "✓ .env.local created from template"
    else
        echo "Warning: .env.example not found, creating empty .env.local"
        touch .env.local
    fi
else
    echo "✓ .env.local already exists"
fi

echo ""
echo "Frontend configuration:"
echo "  API URL: http://localhost:8000/api/v1"
echo ""

echo "================================"
echo "✓ Frontend setup complete!"
echo "================================"
echo ""

echo "Next steps:"
echo ""
echo "1. Start the development server:"
echo "   npm run dev"
echo ""
echo "2. Open http://localhost:5173 in your browser"
echo ""