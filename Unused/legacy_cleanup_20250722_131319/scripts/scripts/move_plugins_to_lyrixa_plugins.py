import os
import shutil

# Set your canonical plugin directory
CANONICAL_PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "lyrixa", "plugins")

# List any old plugin directories here (add more if needed)
OLD_PLUGIN_DIRS = [
    os.path.join(os.path.dirname(__file__), "lyrixa_plugins"),
    # Add other old plugin directories if you find them
]


def move_plugins():
    os.makedirs(CANONICAL_PLUGIN_DIR, exist_ok=True)
    for old_dir in OLD_PLUGIN_DIRS:
        if not os.path.exists(old_dir):
            continue
        for item in os.listdir(old_dir):
            src = os.path.join(old_dir, item)
            dst = os.path.join(CANONICAL_PLUGIN_DIR, item)
            if os.path.exists(dst):
                print(f"[SKIP] {item} already exists in canonical directory.")
                continue
            print(f"[MOVE] {src} -> {dst}")
            shutil.move(src, dst)
        # Optionally remove the old directory if empty
        if not os.listdir(old_dir):
            os.rmdir(old_dir)


if __name__ == "__main__":
    move_plugins()
    print("Plugin migration complete.")
