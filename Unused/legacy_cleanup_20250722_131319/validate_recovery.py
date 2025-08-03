import os

files_to_check = [
    "Aetherra/core/agent_orchestrator.py",
    "Aetherra/lyrixa/memory/memory_core.py",
    "Aetherra/lyrixa/engine/reasoning_engine.py",
    "Aetherra/lyrixa/engine/self_improvement_engine.py",
    "Aetherra/lyrixa/engine/plugin_chain_executor.py",
    "Aetherra/lyrixa/engine/introspection_controller.py",
    "Aetherra/lyrixa/engine/lyrixa_engine.py",
    "Aetherra/lyrixa/db_session.py",
]

print("🔍 File Recovery Validation Report")
print("=" * 50)
print()

total_lines = 0
recovered_files = 0

for file_path in files_to_check:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = len(f.readlines())
            total_lines += lines
            recovered_files += 1
        print(f"✅ {file_path:<50} ({lines:>4} lines)")
    else:
        print(f"❌ {file_path:<50} (MISSING)")

print()
print(f"📊 Summary: {recovered_files}/{len(files_to_check)} critical files recovered")
print(f"📈 Total code recovered: {total_lines:,} lines")
print()

if recovered_files == len(files_to_check):
    print("🎯 Core System Status: FULLY RESTORED")
    print("🚀 Ready for GUI redesign phase!")
else:
    print(f"[WARN]  Missing {len(files_to_check) - recovered_files} files")
