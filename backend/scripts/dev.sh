#!/usr/bin/env bash
set -e

echo "================================"
echo "AI Prompt Firewall - Backend Dev Server"
echo "================================"
echo ""

# Check venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found."
    echo "Run: bash scripts/setup_backend.sh"
    exit 1
fi

# Detect Python command
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
elif command -v py >/dev/null 2>&1; then
    PYTHON_CMD="py"
else
    echo "Error: Python not found"
    exit 1
fi

# Activate virtual environment (cross-platform)
echo "Activating virtual environment..."

if [ -f "venv/Scripts/activate" ]; then
    # Git Bash / Windows
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    # Linux/macOS
    source venv/bin/activate
else
    echo "Error: Cannot find venv activation script"
    exit 1
fi

echo "✓ Virtual environment ready"
echo ""

echo "Starting backend server on http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

# Run server (use python module, not raw uvicorn command)
$PYTHON_CMD -m uvicorn app.main:app --reload --port 8000