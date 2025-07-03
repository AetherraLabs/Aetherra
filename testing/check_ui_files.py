import os
import sys

print("Checking UI files for syntax errors...")
ui_dir = "src/neurocode/ui"
for f in os.listdir(ui_dir):
    if f.endswith(".py"):
        file_path = f"{ui_dir}/{f}"
        print(f"Checking {f}...")
        exit_code = os.system(f"python -m py_compile {file_path}")
        if exit_code != 0:
            print(f"❌ Error in {f}")
        else:
            print(f"✅ {f} is valid")
