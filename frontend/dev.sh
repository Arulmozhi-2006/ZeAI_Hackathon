#!/usr/bin/env bash
set -e

echo "================================"
echo "Frontend Development Server"
echo "================================"
echo ""

# Check Node.js
if ! command -v node >/dev/null 2>&1; then
    echo "Error: Node.js is not installed."
    echo "Install Node.js 18+ from https://nodejs.org"
    exit 1
fi

# Check npm
if ! command -v npm >/dev/null 2>&1; then
    echo "Error: npm is not installed."
    exit 1
fi

NODE_VERSION=$(node -v)
echo "✓ Node $NODE_VERSION detected"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Dependencies not found. Installing..."
    npm install
    echo ""
fi

echo "Starting frontend development server on http://localhost:5173"
echo "Press Ctrl+C to stop"
echo ""

npm run dev