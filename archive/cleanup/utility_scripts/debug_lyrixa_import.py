import importlib.util
import os
import sys

# Add current directory to path
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")
sys.path.insert(0, current_dir)

# Check if Lyrixa directory exists
lyrixa_path = os.path.join(current_dir, "Lyrixa")
print(f"Lyrixa path exists: {os.path.exists(lyrixa_path)}")

# Check if __init__.py exists
init_path = os.path.join(lyrixa_path, "__init__.py")
print(f"Lyrixa __init__.py exists: {os.path.exists(init_path)}")

# Try to load the module spec
try:
    spec = importlib.util.spec_from_file_location("Lyrixa", init_path)
    print(f"Module spec: {spec}")

    if spec:
        module = importlib.util.module_from_spec(spec)
        print(f"Module created: {module}")

        # Try to execute
        spec.loader.exec_module(module)
        print(
            f"Module executed successfully, version: {getattr(module, '__version__', 'No version')}"
        )

except Exception as e:
    print(f"Error loading module: {e}")
    import traceback

    traceback.print_exc()

# Also try direct import
try:
    import Lyrixa

    print(f"Direct import successful: {Lyrixa.__version__}")
except Exception as e:
    print(f"Direct import failed: {e}")
