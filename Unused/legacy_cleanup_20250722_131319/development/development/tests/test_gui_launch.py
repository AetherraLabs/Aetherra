"""
Test GUI Launch - Minimal test to check if our new window loads
"""

import sys
from pathlib import Path

# Add Aetherra to path
aetherra_path = Path(__file__).parent / "Aetherra"
sys.path.insert(0, str(aetherra_path))

try:
    print("🔄 Importing GUI window...")
    from lyrixa.gui.aetherra_main_window import create_aetherra_main_window

    print("✅ Import successful!")
    print("🖥️ Creating GUI window...")

    # Create and show window
    app, window = create_aetherra_main_window()

    print("✅ Window created successfully!")
    print("🚀 Starting application...")

    window.show()

    # Run the app
    sys.exit(app.exec())

except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback

    traceback.print_exc()
