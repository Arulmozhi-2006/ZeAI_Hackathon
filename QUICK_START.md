# Quick Start Guide

## Prerequisites
- Python 3.9+
- Node.js 18+
- Supabase account (free tier works)
- Gemini API key (free tier works)

## 5-Minute Setup

### 1. Clone & Install
```bash
bash setup.sh
```

### 2. Configure Credentials
```bash
# Edit backend/.env
nano backend/.env

# Add your Supabase connection string:
SUPABASE_DB_URL=postgresql://postgres:PASSWORD@db.XXXXX.supabase.co:5432/postgres

# Add your Gemini API key:
GEMINI_API_KEY=your-key-here
```

### 3. Train ML Model (5-10 minutes)
```bash
cd backend
bash scripts/train_model.sh
```

### 4. Start Backend
```bash
# Terminal 1
cd backend
bash scripts/dev.sh
```

### 5. Start Frontend
```bash
# Terminal 2
cd frontend
npm run dev
```

### 6. Open & Test
http://localhost:5173

### 7. Verify Setup
```bash
bash backend/scripts/health_check.sh
```

---

## Test Login
Email: test@example.com

Password: Test123456 (or any password you set)

If login fails → **Check the troubleshooting guide**: SETUP_TROUBLESHOOTING.md
Now update the root README to reference this:
The issue is almost certainly one of:

Backend not running → cd backend && bash scripts/dev.sh
Database not configured → Edit backend/.env with Supabase credentials
API URL wrong → Check frontend/.env.local has VITE_API_URL=http://localhost:8000/api/v1
Database not initialized → Run alembic upgrade head and python -m app.db.seed_data

Test with this curl command:
bashcurl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "full_name": "Test User"
  }'
If this returns a 201 or 409 status, the backend works. If it times out or says "connection refused", the backend isn't running.