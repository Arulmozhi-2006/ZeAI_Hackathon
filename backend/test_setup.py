import sys
import os
from pathlib import Path

print("=" * 60)
print("Backend Setup Diagnostic")
print("=" * 60)

# Test 1: .env file
print("\n1️⃣  Checking .env file...")
env_file = Path("backend/.env")
if env_file.exists():
    print("   ✅ .env file exists")
    with open(env_file) as f:
        for line in f:
            if not line.startswith("#"):
                key = line.split("=")[0]
                print(f"      - {key}")
else:
    print("   ❌ .env file NOT found")
    sys.exit(1)

# Test 2: Load config
print("\n2️⃣  Loading config...")
try:
    from app.core.config import settings
    print("   ✅ Config loaded")
    print(f"      - DB URL: {settings.SUPABASE_DB_URL[:30]}...")
    print(f"      - Allowed Origins: {settings.allowed_origins_list}")
except Exception as e:
    print(f"   ❌ Config load failed: {e}")
    sys.exit(1)

# Test 3: Database connection
print("\n3️⃣  Testing database connection...")
try:
    from app.db.session import engine
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("   ✅ Database connected")
except Exception as e:
    print(f"   ❌ Database connection failed: {e}")
    print("      Check SUPABASE_DB_URL in .env")
    sys.exit(1)

# Test 4: Models
print("\n4️⃣  Checking models...")
try:
    from app.models.user import User
    from app.models.threat_category import ThreatCategory
    print("   ✅ Models imported")
except Exception as e:
    print(f"   ❌ Model import failed: {e}")
    sys.exit(1)

# Test 5: API routes
print("\n5️⃣  Checking API routes...")
try:
    from app.api.v1.router import api_router
    print("   ✅ API router loaded")
    print(f"      Routes: {len(api_router.routes)}")
except Exception as e:
    print(f"   ❌ API router load failed: {e}")
    sys.exit(1)

# Test 6: Main app
print("\n6️⃣  Checking main app...")
try:
    from app.main import app
    print("   ✅ Main app loaded")
except Exception as e:
    print(f"   ❌ Main app load failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All checks passed! Backend is ready.")
print("=" * 60)
print("\nStart with:")
print("  uvicorn app.main:app --reload --port 8000")