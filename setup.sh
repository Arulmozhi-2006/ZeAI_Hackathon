# # #!/usr/bin/env bash
# # set -e

# # echo "=========================================="
# # echo "AI Prompt Firewall - Complete Setup"
# # echo "=========================================="
# # echo ""

# # # Setup backend
# # echo "Setting up backend..."
# # cd backend
# # bash scripts/setup_backend.sh
# # cd ..
# # echo ""

# # # Setup frontend
# # echo "Setting up frontend..."
# # cd frontend
# # bash setup.sh
# # cd ..
# # echo ""

# # echo "=========================================="
# # echo "✓ Complete setup finished!"
# # echo "=========================================="
# # echo ""
# # echo "NEXT STEPS:"
# # echo ""
# # echo "1. Configure credentials:"
# # echo "   - Edit backend/.env with Supabase credentials"
# # echo "   - Add your GEMINI_API_KEY to backend/.env"
# # echo ""
# # echo "2. Train the ML model (5-10 minutes):"
# # echo "   cd backend"
# # echo "   bash scripts/train_model.sh"
# # echo ""
# # echo "3. Start the application in separate terminals:"
# # echo ""
# # echo "   Terminal 1 - Backend:"
# # echo "   cd backend"
# # echo "   bash scripts/dev.sh"
# # echo ""
# # echo "   Terminal 2 - Frontend:"
# # echo "   cd frontend"
# # echo "   bash dev.sh"
# # echo ""
# # echo "4. Open http://localhost:5173 in your browser"
# # echo ""
# # echo "5. Create an account and start testing!"
# # echo ""
# # echo "For more details, see README.md"
# # echo "=========================================="

# #!/usr/bin/env bash
# set -e

# echo "=========================================="
# echo "AI Prompt Firewall - Complete Setup"
# echo "=========================================="
# echo ""

# # Detect bash availability (important for Windows environments)
# if ! command -v bash >/dev/null 2>&1; then
#     echo "Error: Bash is required. Please use Git Bash or WSL."
#     exit 1
# fi

# # Detect Python early (optional sanity check)
# if command -v python3 >/dev/null 2>&1; then
#     PYTHON_CMD="python3"
# elif command -v python >/dev/null 2>&1; then
#     PYTHON_CMD="python"
# elif command -v py >/dev/null 2>&1; then
#     PYTHON_CMD="py"
# else
#     echo "Warning: Python not detected yet. Backend setup will validate it."
# fi

# # Setup backend
# echo "Setting up backend..."
# cd backend

# if [ -f "scripts/setup_backend.sh" ]; then
#     bash scripts/setup_backend.sh
# else
#     echo "Error: backend setup script not found"
#     exit 1
# fi

# cd ..
# echo ""

# # Setup frontend
# echo "Setting up frontend..."
# cd frontend

# if [ -f "setup.sh" ]; then
#     bash setup.sh
# else
#     echo "Error: frontend setup script not found"
#     exit 1
# fi

# cd ..
# echo ""

# echo "=========================================="
# echo "✓ Complete setup finished!"
# echo "=========================================="
# echo ""

# echo "NEXT STEPS:"
# echo ""
# echo "1. Configure credentials:"
# echo "   - Edit backend/.env with Supabase credentials"
# echo "   - Add your GEMINI_API_KEY to backend/.env"
# echo ""

# echo "2. Train the ML model (5-10 minutes):"
# echo "   cd backend"
# echo "   bash scripts/train_model.sh"
# echo ""

# echo "3. Start the application in separate terminals:"
# echo ""
# echo "   Terminal 1 - Backend:"
# echo "   cd backend"
# echo "   bash scripts/dev.sh"
# echo ""
# echo "   Terminal 2 - Frontend:"
# echo "   cd frontend"
# echo "   bash dev.sh"
# echo ""

# echo "4. Open http://localhost:5173 in your browser"
# echo ""
# echo "5. Create an account and start testing!"
# echo ""
# echo "For more details, see README.md"
# echo "=========================================="

#!/usr/bin/env bash
set -e

echo "=========================================="
echo "AI Prompt Firewall - Complete Setup"
echo "=========================================="
echo ""

# Detect bash availability (important for Windows environments)
if ! command -v bash >/dev/null 2>&1; then
    echo "Error: Bash is required. Please use Git Bash or WSL."
    exit 1
fi

# Detect Python early (optional sanity check)
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
elif command -v py >/dev/null 2>&1; then
    PYTHON_CMD="py"
else
    echo "Warning: Python not detected yet. Backend setup will validate it."
fi

# Setup backend
echo "Setting up backend..."
cd backend

if [ -f "scripts/setup_backend.sh" ]; then
    bash scripts/setup_backend.sh
else
    echo "Error: backend setup script not found"
    exit 1
fi

cd ..
echo ""

# Setup frontend
echo "Setting up frontend..."
cd frontend

if [ -f "setup.sh" ]; then
    bash setup.sh
else
    echo "Error: frontend setup script not found"
    exit 1
fi

cd ..
echo ""

echo "=========================================="
echo "✓ Complete setup finished!"
echo "=========================================="
echo ""

echo "NEXT STEPS:"
echo ""
echo "1. Configure credentials:"
echo "   - Edit backend/.env with Supabase credentials"
echo "   - Add your GEMINI_API_KEY to backend/.env"
echo ""

echo "2. Train the ML model (5-10 minutes):"
echo "   cd backend"
echo "   bash scripts/train_model.sh"
echo ""

echo "3. Start the application in separate terminals:"
echo ""
echo "   Terminal 1 - Backend:"
echo "   cd backend"
echo "   bash scripts/dev.sh"
echo ""
echo "   Terminal 2 - Frontend:"
echo "   cd frontend"
echo "   bash dev.sh"
echo ""

echo "4. Open http://localhost:5173 in your browser"
echo ""
echo "5. Create an account and start testing!"
echo ""
echo "For more details, see README.md"
echo "=========================================="