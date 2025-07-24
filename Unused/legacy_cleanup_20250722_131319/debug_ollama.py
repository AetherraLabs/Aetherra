"""
Debug Ollama API Response
Check what the actual response format is
"""

try:
    import ollama

    print("🔍 Checking Ollama API response format...")

    client = ollama.Client()
    models = client.list()

    print(f"📋 Raw response: {models}")
    print(f"📋 Type: {type(models)}")

    if isinstance(models, dict) and "models" in models:
        print(f"📋 Models array: {models['models']}")
        for model in models["models"]:
            print(f"   🔸 Model entry: {model}")
            print(f"      Type: {type(model)}")
            if isinstance(model, dict):
                print(f"      Keys: {list(model.keys())}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
