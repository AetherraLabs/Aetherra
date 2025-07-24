"""
Lyrixa Modular Launcher — The Philosopher's Core
Auto-discovers and integrates all valid .py, .aether, and .aetherplugin files
across the Aetherra project.

Written for: Aetherra AI OS
"""

import importlib.util
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# 🔧 CRITICAL FIX: Global variable to prevent window garbage collection
_main_window_instance = None

# Configure matplotlib early to prevent font spam
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-interactive backend
    import matplotlib.pyplot as plt

    plt.ioff()  # Turn off interactive mode

    # Suppress font logging
    import logging

    logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
except ImportError:
    pass  # matplotlib not available

# ========== CONFIGURATION ==========
DEBUG_MODE = True
LOG_FILE = "launcher_debug.log"

IGNORED_FOLDERS = [
    ".git",
    ".github",
    ".vscode",
    ".vite",
    ".plugin_history",
    ".safe_backups",
    ".aether",
    "backups",
    "docs",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    "site-packages",
    ".pytest_cache",
    ".mypy_cache",
    ".coverage",
    "htmlcov",
    "dist",
    "build",
    "egg-info",
    "Aetherra Website",  # Exclude the Aetherra Website folder
]

VALID_EXTENSIONS = [".py", ".aether", ".aetherplugin", ".json"]
# Removed DEFAULT_ENTRYPOINT since we don't want to force execution

# ========== LOGGING SETUP ==========
logging.basicConfig(
    filename=LOG_FILE if DEBUG_MODE else None,
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(message)s"))
logging.getLogger().addHandler(console_handler)


# ========== PLACEHOLDER REGISTRIES ==========
# Global variables to store loaded and unlinked features for external use
last_loaded = []
last_unlinked = []
plugin_manager = {}
workflow_registry = {}
unlinked_features = []

# ========== STATUS REPORTING ==========


def write_launcher_status_report(
    loaded, unlinked, output_path="launcher_status_report.json"
):
    report = {
        "timestamp": datetime.now().isoformat(),
        "loaded_features": loaded,
        "unlinked_features": unlinked,
        "summary": {
            "total_loaded": len(loaded),
            "total_unlinked": len(unlinked),
            "success_rate": round(
                len(loaded) / max(1, (len(loaded) + len(unlinked))), 2
            ),
        },
    }
    try:
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        logging.info(f"[✓] Status report saved to {output_path}")
    except Exception as e:
        logging.error(f"[ERROR] Failed to write status report: {e}")


# ========== DISCOVERY LOGIC ==========
def discover_all_files(base_path="."):
    """
    Discover all valid files within the Aetherra Project directory only.

    Args:
        base_path (str): Base path to start scanning from

    Returns:
        list: List of Path objects for discovered files
    """
    files = []

    # Convert base_path to absolute path and ensure it's within Aetherra Project
    base_path = Path(base_path).resolve()

    # Define the Aetherra Project root directory
    aetherra_project_root = Path(__file__).resolve().parent.parent.parent

    # Ensure we're only scanning within the Aetherra Project directory
    try:
        # Check if base_path is within aetherra_project_root
        base_path.relative_to(aetherra_project_root)
    except ValueError:
        # If base_path is outside Aetherra Project, use Aetherra Project root
        logging.warning(
            f"Base path {base_path} is outside Aetherra Project. Using project root instead."
        )
        base_path = aetherra_project_root

    logging.info(f"🔍 Scanning files within: {base_path}")

    for root, dirs, filenames in os.walk(base_path):
        root_path = Path(root)

        # Ensure we don't scan outside the Aetherra Project directory
        try:
            root_path.relative_to(aetherra_project_root)
        except ValueError:
            continue  # Skip directories outside the project

        # Remove ignored directories from dirs list to prevent walking into them
        dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS]

        # Skip if current path contains any ignored folder parts (including nested paths)
        root_str = str(root).lower()
        if any(ignored.lower() in root_str for ignored in IGNORED_FOLDERS):
            continue

        # Additional specific check for Aetherra Website folder path
        if "aetherra website" in root_str or "aetherra_website" in root_str:
            continue

        # Skip if we're in a site-packages or similar directory
        if "site-packages" in root or ".venv" in root or "venv" in root:
            continue

        for filename in filenames:
            if any(filename.endswith(ext) for ext in VALID_EXTENSIONS):
                # Filter out problematic files during discovery
                filename_lower = filename.lower()

                # Skip demo files (but allow critical system files)
                if filename_lower.startswith("demo") and not filename_lower.startswith("demo_"):
                    continue

                # Skip test files - but be more selective
                test_patterns = [
                    "test_",
                    "_test.py",
                    "conftest",
                    "pytest",
                    "unittest",
                ]
                if any(pattern in filename_lower for pattern in test_patterns):
                    continue

                # Only skip truly problematic prefixes, not system components
                problematic_starts = [
                    "apply_",
                    "clean_",
                    "clear_",
                    "diagnose_",
                    "emergency_",
                    "fix_",
                    "lightweight_",
                    "minimal_",
                    "quick_",
                ]

                if any(
                    filename_lower.startswith(prefix) for prefix in problematic_starts
                ):
                    continue

                full_path = Path(root) / filename
                # Additional check to avoid problematic files
                if not any(ignored in str(full_path) for ignored in IGNORED_FOLDERS):
                    files.append(full_path)
    return files


# ========== HELPER FUNCTIONS ==========
def parse_manifest(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.warning(f"[WARN] Failed to parse manifest {file_path.name}: {e}")
        return {}


def infer_type(path):
    name = path.name.lower()
    if "plugin" in name:
        return "plugin"
    elif "workflow" in name or path.suffix == ".aether":
        return "workflow"
    elif "agent" in name:
        return "agent"
    return "unknown"


def load_python_module(file_path):
    try:
        # Skip files that are clearly not meant to be loaded as modules
        file_str = str(file_path)
        file_name = file_path.name.lower()

        # Only skip actual test files, not system components
        test_patterns = [
            "test_",
            "_test.py",
            "conftest",
            "pytest",
            "unittest",
        ]
        if any(pattern in file_name for pattern in test_patterns):
            return None

        # Only skip truly problematic files, not system components
        problematic_starts = [
            "apply_",
            "clean_",
            "clear_",
            "diagnose_",
            "emergency_",
            "fix_",
            "minimal_",
            "quick_",
        ]

        if any(file_name.startswith(prefix) for prefix in problematic_starts):
            return None

        # Much more targeted skip patterns - only skip obvious non-modules
        skip_patterns = [
            "site-packages",
            ".venv",
            "venv",
            "__pycache__",
            "setup.py",
            "conftest",
            "pytest",
            "unittest",
            "_backup",
            "backup_",
            "_old",
            "_archive",
            "temp_",
            "_temp",
            "tmp_",
            "_tmp",
            "broken",
            "hotfix",
            "readme",
            "changelog",
            "migration",
            "upgrade",
            "downgrade",
        ]

        # Check file path patterns - be much more selective
        if any(skip_pattern in file_str.lower() for skip_pattern in skip_patterns):
            return None

        # Don't skip files just because they contain certain words
        # Only skip if they start with problematic prefixes
        if file_name.startswith(
            (
                "test_",
                "backup_",
                "temp_",
                "tmp_",
                "fix_",
            )
        ):
            return None

        # Don't skip files that end with certain suffixes unless they're clearly temp files
        name_without_ext = file_path.stem.lower()
        if name_without_ext.endswith(
            (
                "_backup",
                "_old",
                "_archive",
                "_temp",
                "_tmp",
            )
        ):
            return None

        # NEW: Smart module loading - handle relative imports gracefully
        # Try to determine if this is part of a package structure
        try:
            # First, try to load it as a regular module
            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            if spec is None or spec.loader is None:
                return None

            module = importlib.util.module_from_spec(spec)

            # Add the parent directory to sys.path temporarily to help with imports
            parent_dir = str(file_path.parent)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
                try:
                    spec.loader.exec_module(module)
                    return module
                finally:
                    # Remove the path after loading
                    if parent_dir in sys.path:
                        sys.path.remove(parent_dir)
            else:
                spec.loader.exec_module(module)
                return module

        except ImportError as e:
            # If it's a relative import error, just log it as a warning instead of error
            if "attempted relative import" in str(e):
                logging.warning(f"[WARN] Module {file_path.name} has relative imports - skipping: {e}")
                return None
            else:
                # Re-raise other import errors
                raise e

    except Exception as e:
        # Only log as error if it's not a relative import issue
        if "attempted relative import" in str(e):
            logging.warning(f"[WARN] Skipping module with relative imports: {file_path.name}")
        else:
            logging.error(f"[ERROR] Failed to load module {file_path}: {e}")
        return None


# ========== CORE INTEGRATION LOGIC ==========
def integrate_feature(file, metadata=None):
    metadata = metadata or {}
    ftype = metadata.get("type") or infer_type(file)
    entry = metadata.get("entry", None)  # Don't force an entry point

    if file.suffix == ".py":
        mod = load_python_module(file)
        if mod:
            # Check if there's a specific entry point to call
            if entry and hasattr(mod, entry):
                try:
                    getattr(mod, entry)()
                    logging.info(f"[✓] Executed {ftype}: {file.name} -> {entry}()")
                except Exception as e:
                    logging.error(
                        f"[ERROR] Execution failed in {file.name}.{entry}(): {e}"
                    )
            else:
                # Module loaded successfully, no specific entry point needed
                logging.info(f"[✓] Loaded {ftype}: {file.name}")
        else:
            logging.debug(f"[~] Failed to load module: {file.name}")
            unlinked_features.append(str(file))

    elif file.suffix == ".aether":
        try:
            # Future connection to Aether runtime
            workflow_registry[file.stem] = str(file)
            logging.info(f"[~] Registered Aether script: {file.name}")
        except Exception as e:
            logging.warning(f"[!] Failed to register Aether script: {file.name}: {e}")
            unlinked_features.append(str(file))

    else:
        logging.debug(f"[~] Unknown type or unsupported: {file.name}")
        unlinked_features.append(str(file))


# ========== MAIN LAUNCHER ==========
def launch_all_features(project_root="Aetherra", gui_mode=False, api_mode=False):
    """
    Launch all Aetherra features

    Args:
        project_root (str): Path to the project root (defaults to "Aetherra" directory)
        gui_mode (bool): Set to True if running in GUI mode
        api_mode (bool): Set to True if running with API server

    Returns:
        tuple: (loaded_modules, unlinked_modules) for external use
    """
    global last_loaded, last_unlinked

    logging.info("🚀 [Aetherra] Launching Modular System Scan...")
    all_files = discover_all_files(project_root)

    for file in all_files:
        if file.suffix == ".aetherplugin":
            metadata = parse_manifest(file)
            entry_file = file.with_name(metadata.get("entry_file", ""))
            if entry_file.exists():
                integrate_feature(entry_file, metadata)
            else:
                logging.warning(f"[WARN] Entry file missing for manifest: {file.name}")
        else:
            integrate_feature(file)

    if unlinked_features:
        logging.warning(f"\n[!] Unlinked Features ({len(unlinked_features)}):")
        for f in unlinked_features:
            logging.warning(" - " + f)

    # Final sanity/self-check
    try:
        from lyrixa.core import run_self_check

        run_self_check()
        logging.info("[✓] Lyrixa system check completed.")
    except ImportError:
        logging.info("[i] Lyrixa core check not available — skipping.")
    except Exception as e:
        logging.error(f"[!] Lyrixa check failed: {e}")

    loaded_names = list(
        set(file.name for file in all_files if str(file) not in unlinked_features)
    )
    write_launcher_status_report(loaded_names, unlinked_features)
    logging.info("🚀 [Aetherra] Modular System Scan Complete!")

    # Update global variables for external access
    last_loaded = loaded_names
    last_unlinked = unlinked_features

    # Return results for direct use
    return loaded_names, unlinked_features


# ========== API COMPATIBILITY FUNCTIONS ==========
def initialize_system(project_root="Aetherra", gui_mode=False, api_mode=False):
    """
    Initialize the Aetherra system

    This function provides backward compatibility with code that expects
    an initialize_system function. It's an enhanced version of launch_all_features
    that also initializes the API server if requested.

    Args:
        project_root (str): Path to the project root (defaults to "Aetherra" directory)
        gui_mode (bool): Set to True if running in GUI mode
        api_mode (bool): Set to True if running the API server

    Returns:
        tuple: (loaded_modules, unlinked_modules, api_server) for external use
    """
    import sys  # Import sys here for use in this function

    loaded_modules, unlinked_modules = launch_all_features(project_root, gui_mode)
    api_server = None

    # Initialize GUI if requested
    if gui_mode:
        try:
            logging.info("🖥️ Initializing Lyrixa GUI...")

            # Check if user wants web interface or Qt interface
            use_web_interface = "--web" in sys.argv or (
                "--qt" not in sys.argv and gui_mode
            )  # Default to web interface unless Qt is specifically requested

            if use_web_interface:
                logging.info("🌐 Starting web-based neural interface...")
                try:
                    from Aetherra.lyrixa.gui.web_interface_server import start_web_interface

                    # Start web interface in a separate thread if API mode is also enabled
                    if api_mode:
                        import threading
                        web_thread = threading.Thread(
                            target=start_web_interface,
                            kwargs={'host': '127.0.0.1', 'port': 8686, 'auto_open': True}
                        )
                        web_thread.daemon = True
                        web_thread.start()
                        logging.info("✅ Web interface started in background thread")
                    else:
                        # Start web interface directly (this will block)
                        start_web_interface(host='127.0.0.1', port=8686, auto_open=True)

                except ImportError as e:
                    logging.error(f"❌ Failed to import web interface: {e}")
                    use_web_interface = False

            if not use_web_interface or "--qt" in sys.argv:
                # Fall back to Qt interface or use Qt if specifically requested
                logging.info("🖥️ Using Qt-based interface...")
                import sys
                from PySide6.QtWidgets import QApplication

                # Create QApplication if it doesn't exist
                app = QApplication.instance()
                if not app:
                    app = QApplication(sys.argv)

                # Import and create the Qt neural interface
                try:
                    from Aetherra.lyrixa.gui.aetherra_neural_interface import (
                        create_aetherra_neural_interface,
                    )

                    app, window = create_aetherra_neural_interface()

                    # 🔧 CRITICAL FIX: Store window as instance variable to prevent garbage collection
                    global _main_window_instance
                    _main_window_instance = window

                    window.show()

                    logging.info("✅ Qt Neural Interface initialized successfully")

                    # If not in API mode, run the event loop
                    if not api_mode:
                        logging.info("🚀 Starting Qt GUI event loop...")
                        app.exec()

                except ImportError as e:
                    logging.error(f"❌ Failed to import Qt interface: {e}")
                    logging.info("💡 Suggestion: Use --web mode for web-based interface")

        except Exception as e:
            logging.error(f"❌ Failed to initialize GUI: {e}")
            import traceback
            traceback.print_exc()

    # Initialize API server if requested
    if api_mode:
        try:
            logging.info("🌐 Initializing API server...")
            try:
                # Try to import from lyrixa.fixed_api_server first (preferred)
                from lyrixa.fixed_api_server import initialize_api_server

                api_server = initialize_api_server()
                logging.info("✅ API server initialized from fixed_api_server")
            except ImportError:
                # Fall back to other possible locations
                try:
                    from lyrixa.core.api_server import initialize_api_server

                    api_server = initialize_api_server()
                    logging.info("✅ API server initialized from core.api_server")
                except ImportError:
                    logging.warning("⚠️ Could not import API server module")
        except Exception as e:
            logging.error(f"❌ Failed to initialize API server: {e}")

    return loaded_modules, unlinked_modules, api_server


# Function to get plugin paths for GUI
def get_plugin_paths():
    """
    Return a list of all plugin paths discovered by the launcher

    Returns:
        list: Paths to all discovered plugins
    """
    # In a real implementation, you would track all plugin paths
    # For now, we'll return a default list
    return ["lyrixa.plugins", "Aetherra/plugins"]


# ========== ENTRY POINT ==========
if __name__ == "__main__":
    import sys

    # Parse command line arguments
    api_mode = "--api" in sys.argv
    standalone_mode = "--standalone" in sys.argv
    web_mode = "--web" in sys.argv
    qt_mode = "--qt" in sys.argv

    # Default to web-based GUI unless specific mode is requested
    gui_mode = "--gui" in sys.argv or web_mode or (
        not api_mode and not standalone_mode and not qt_mode
    )

    print("🚀 Aetherra Launcher v6.0 - Lyrixa Cognitive OS")
    print("=" * 50)

    if web_mode or (gui_mode and not qt_mode):
        print("🌐 Mode: Web-based Neural Interface (Recommended)")
        print("📍 URL: http://localhost:8686")
    elif qt_mode:
        print("🖥️  Mode: Qt-based Desktop Interface")
    elif api_mode:
        print("🔗 Mode: API Server")
    elif standalone_mode:
        print("⚙️  Mode: Standalone (No GUI)")

    print("=" * 50)

    # Initialize the system with appropriate modes - use Aetherra directory by default
    initialize_system("Aetherra", gui_mode=gui_mode, api_mode=api_mode)

    if not (api_mode or gui_mode):
        print("\n✅ Aetherra launcher initialized in standalone mode")
        print("💡 Available modes:")
        print("   --web     Web-based neural interface (recommended)")
        print("   --qt      Qt-based desktop interface")
        print("   --gui     Default GUI mode (web-based)")
        print("   --api     API server mode")
        print("   --standalone  No GUI mode")
