#!/usr/bin/env bash
set -e

echo "================================"
echo "Training ML Model"
echo "================================"
echo ""

# Check venv exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Run: bash scripts/setup_backend.sh first."
    exit 1
fi

# Detect Python
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

# Activate venv safely (Windows + Linux)
echo "Activating virtual environment..."

if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: Cannot find virtual environment activation script"
    exit 1
fi

echo "✓ Virtual environment ready"
echo ""

echo "Downloading datasets and training XGBoost model..."
echo "This will take 5-10 minutes on first run."
echo ""

# Run training using correct interpreter
$PYTHON_CMD -m app.ml.trainer

echo ""
echo "✓ Model training complete!"
echo ""