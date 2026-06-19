import os
import json

stubs = []
keywords = [
    'raise NotImplementedError',
    'pass  # stub',
    '# TODO:',
    '# FIXME:',
]

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['.git', '.venv', 'node_modules', 'dist-packages', '__pycache__', '.pytest_cache', 'archive', 'demos', 'experiments']]
    
    for file in files:
        if not file.endswith('.py'):
            continue
        
        filepath = os.path.join(root, file)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    for kw in keywords:
                        if kw in line:
                            stubs.append({'file': filepath.replace(chr(92), '/'), 'line': i, 'type': kw})
                            break
        except:
            pass

# Save to file
with open('STUB_INVENTORY.json', 'w') as f:
    json.dump({'total': len(stubs), 'stubs': stubs[:100]}, f, indent=2)

print(f'Found {len(stubs)} critical stubs (raise NotImplementedError, TODO, FIXME, pass # stub)')
