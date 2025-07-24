#!/usr/bin/env python3
"""
🔧 Aetherra Project Maintenance Script
====================================

Regular maintenance tasks for keeping the project clean and organized.
Run this script periodically to maintain project health.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def quick_cleanup():
    """Perform quick cleanup of common clutter."""
    project_root = Path(__file__).parent.parent
    removed_count = 0
    
    # Remove Python cache
    for pycache in project_root.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache)
            removed_count += 1
        except Exception:
            pass
    
    # Remove temporary files
    temp_patterns = ["*.tmp", "*.temp", "*.log"]
    for pattern in temp_patterns:
        for temp_file in project_root.rglob(pattern):
            try:
                temp_file.unlink()
                removed_count += 1
            except Exception:
                pass
    
    print(f"🧹 Quick cleanup complete: {removed_count} items removed")

if __name__ == "__main__":
    quick_cleanup()
