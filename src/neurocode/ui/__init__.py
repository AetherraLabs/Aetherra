"""
NeuroCode UI Package
User interface components and launchers
"""


def launch_gui():
    """Launch the default Neuroplex GUI"""
    try:
        from .neuroplex_fully_modular import main as launch_modular

        return launch_modular()
    except ImportError:
        try:
            from .neuroplex_gui_v2 import main as launch_v2

            return launch_v2()
        except ImportError:
            try:
                from .neuro_ui import main as launch_basic

                return launch_basic()
            except ImportError:
                print("❌ No GUI modules available")
                return None


__all__ = ["launch_gui"]
