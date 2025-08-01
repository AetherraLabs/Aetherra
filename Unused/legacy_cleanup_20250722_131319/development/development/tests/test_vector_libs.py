"""
Test Vector Libraries
Check if torch and sentence-transformers are working
"""

print("🔍 Testing vector library imports...")

try:
    import torch

    print(f"✅ torch: {torch.__version__}")
    torch_ok = True
except Exception as e:
    print(f"❌ torch failed: {e}")
    torch_ok = False

try:
    import sentence_transformers

    print(f"✅ sentence-transformers: {sentence_transformers.__version__}")
    st_ok = True
except Exception as e:
    print(f"❌ sentence-transformers failed: {e}")
    st_ok = False

try:
    import faiss

    print(f"✅ faiss: {faiss.__version__}")
    faiss_ok = True
except Exception as e:
    print(f"❌ faiss failed: {e}")
    faiss_ok = False

print(f"\n📊 Results:")
print(f"   torch: {'✅' if torch_ok else '❌'}")
print(f"   sentence-transformers: {'✅' if st_ok else '❌'}")
print(f"   faiss: {'✅' if faiss_ok else '❌'}")

if torch_ok and st_ok and faiss_ok:
    print("\n🎉 All vector libraries working! The warning is incorrect.")
else:
    print(
        f"\n⚠️ Vector support limited. Missing: {', '.join([lib for lib, ok in [('torch', torch_ok), ('sentence-transformers', st_ok), ('faiss', faiss_ok)] if not ok])}"
    )
