# Standard library imports
import difflib
import pathlib

# Updated to reflect migration: keep reference for legacy diff only if file still exists
target_file = pathlib.Path("aetherra_hub_server.py")
if target_file.exists():
    cur = target_file.read_text(errors="ignore").splitlines()
else:
    cur = []
clean = pathlib.Path("clean_hub_tmp.py").read_text(errors="ignore").splitlines()
for i, line in enumerate(difflib.unified_diff(clean, cur, "HEAD", "WORKING")):
    print(line)
    if i > 300:
        break
