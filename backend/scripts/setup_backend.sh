#!/usr/bin/env bash
set -e

echo "================================"
echo "AI Prompt Firewall - Backend Setup"
echo "================================"
echo ""

# Detect Python
echo "Checking Python version..."

if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
elif command -v py >/dev/null 2>&1; then
    PYTHON_CMD="py"
else
    echo "Error: Python 3.9 or higher is not installed."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment (cross-platform)
echo "Activating virtual environment..."

if [ -f "venv/Scripts/activate" ]; then
    # Windows Git Bash
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    # Linux/macOS
    source venv/bin/activate
else
    echo "Error: Cannot find virtual environment activation script"
    exit 1
fi

echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --quiet --upgrade pip setuptools wheel
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."
python -m pip install --quiet -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit the .env file with your credentials:"
    echo "   - SUPABASE_DB_URL"
    echo "   - GEMINI_API_KEY"
    echo "   - JWT_SECRET_KEY"
    echo ""
else
    echo "✓ .env file already exists"
fi

# Create model directory
echo "Creating model artifact directory..."
mkdir -p app/ml/models_store
echo "✓ Model directory created"
echo ""

# Run database migrations
echo "Running database migrations..."
$PYTHON_CMD -m alembic upgrade head
echo "✓ Database migrations applied"
echo ""

# Seed threat categories
echo "Seeding threat categories..."
$PYTHON_CMD -m app.db.seed_data
echo "✓ Threat categories seeded"
echo ""

echo "================================"
echo "✓ Backend setup complete!"
echo "================================"
echo ""

echo "Next steps:"
echo "1. Edit .env with your credentials (Supabase, Gemini API key)"
echo "2. Train the ML model:"
echo "   python -m app.ml.trainer"
echo ""
echo "3. Start the backend server:"
echo "   uvicorn app.main:app --reload --port 8000"
echo ""