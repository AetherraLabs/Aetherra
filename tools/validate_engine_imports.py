import importlib
import sys

modules = [
    "Aetherra.aetherra_core.engine.aetherra_engine",
    "Aetherra.aetherra_core.engine.lyrixa_engine",
    "cosmic_consciousness_engine",
    "Aetherra.consciousness.cosmic.cosmic_consciousness_engine",
    "Aetherra.consciousness.quantum.quantum_consciousness_engine",
]

failed = []
for m in modules:
    try:
        importlib.import_module(m)
        print(f"OK: {m}")
    except Exception as e:
        print(f"FAIL: {m}: {e}")
        failed.append((m, str(e)))

if failed:
    sys.exit(1)
