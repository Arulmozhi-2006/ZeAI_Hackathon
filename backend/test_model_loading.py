import logging
logging.basicConfig(level=logging.INFO)

print("=" * 60)
print("Testing ML Pipeline Loading")
print("=" * 60)

# Test 1: Import engine
print("\n1️⃣  Testing engine import...")
try:
    from app.ml.engine import run_detection
    print("✅ Engine imported successfully")
except Exception as e:
    print(f"❌ Engine import failed: {e}")
    exit(1)

# Test 2: Import embedder
print("\n2️⃣  Testing embedder...")
try:
    from app.ml.embedder import get_embedding
    print("✅ Embedder imported")
except Exception as e:
    print(f"❌ Embedder import failed: {e}")
    exit(1)

# Test 3: Test embedder initialization (THIS WILL DOWNLOAD MODEL)
print("\n3️⃣  Testing embedder initialization (may take 1-2 minutes on first run)...")
try:
    print("   Loading MiniLM-L6-v2 model from HuggingFace...")
    embedding = get_embedding("hello world", model_name="all-MiniLM-L6-v2")
    print(f"   ✅ Embedding created: shape {embedding.shape}")
except Exception as e:
    print(f"   ❌ Embedder initialization failed: {e}")
    exit(1)

# Test 4: Import classifier
print("\n4️⃣  Testing classifier...")
try:
    from app.ml.classifier import predict, CATEGORY_NAMES
    print(f"✅ Classifier imported. Categories: {CATEGORY_NAMES}")
except Exception as e:
    print(f"❌ Classifier import failed: {e}")
    exit(1)

# Test 5: Full detection
print("\n5️⃣  Testing full detection pipeline...")
try:
    print("   Running detection on test prompt...")
    result = run_detection("hello world")
    print(f"   ✅ Detection successful!")
    print(f"      - Category: {result.category_name}")
    print(f"      - Risk Score: {result.risk_score}")
    print(f"      - Time: {result.inference_time_ms:.0f}ms")
except Exception as e:
    print(f"   ❌ Detection failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! Model pipeline is working.")
print("=" * 60)