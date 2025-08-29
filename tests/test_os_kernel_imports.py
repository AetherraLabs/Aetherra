import importlib


def test_os_kernel_imports_available():
    mod = importlib.import_module("Aetherra.aetherra_core.os_kernel")
    assert hasattr(mod, "AetherraKernelLoop")
    assert hasattr(mod, "get_kernel")
    assert hasattr(mod, "HMRController")
    assert hasattr(mod, "get_hmr_controller")
