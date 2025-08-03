# Aetherra Canonical Import Map

This document provides a comprehensive mapping of all valid, deprecated, and recommended import paths for the Aetherra project. Use this as a reference to ensure all code adheres to the modular import structure.

---

## [DISC] Canonical Import Prefixes

- `Aetherra.`
- `Lyrixa.`
- `aetherra_core.`
- `lyrixa_core.`
- Relative imports (e.g., `from .module import X`)

---

## [OK] Valid Imports (Canonical Examples)

```python
from aetherra_core.memory.fractal_encoder import FractalEncoder
from lyrixa_core.plugins.plugin_manager import PluginManager
from Aetherra.plugins.agent_adapters.agent_base import AgentBase
from Lyrixa.intelligence import LyrixaIntelligence
```

---

## 🚫 Deprecated/Legacy Imports

```python
from core.plugin_api import register_plugin  # Deprecated
from lyrixa.plugins import PluginManager    # Deprecated path
from plugins.agent_base import AgentBase    # Deprecated path
```

**Do not use absolute imports outside the canonical namespaces.**

---

## 🔄 Migration Guide

| Deprecated Import Path                        | Canonical Replacement                                              |
| --------------------------------------------- | ------------------------------------------------------------------ |
| `from core.plugin_api import register_plugin` | `from aetherra_core.plugins.plugin_api import register_plugin`     |
| `from lyrixa.plugins import PluginManager`    | `from lyrixa_core.plugins.plugin_manager import PluginManager`     |
| `from plugins.agent_base import AgentBase`    | `from Aetherra.plugins.agent_adapters.agent_base import AgentBase` |

---

## 🛠️ How to Check Imports

- Use the `verify_imports.py` script to automatically check for non-canonical imports:

  ```bash
  python verify_imports.py
  ```

- All new code and pull requests **must** pass this check.

---

## 📚 See Also

- [README.md](../README.md#modular-import-structure)
- [verify_imports.py](../verify_imports.py)
- [docs/architecture.md](architecture.md)

---

_Last updated: July 31, 2025_
