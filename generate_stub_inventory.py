import os
import json

stubs = []
keywords = [
    'raise NotImplementedError',
    'pass  # stub',
    '# TODO:',
    '# FIXME:',
]

skip_dirs = {'.git', '.venv', 'node_modules', 'dist-packages', '__pycache__', '.pytest_cache', 'archive', 'demos', 'experiments'}

count = 0
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    
    for file in files:
        if not file.endswith('.py'):
            continue
        
        filepath = os.path.join(root, file)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    for kw in keywords:
                        if kw in line:
                            stubs.append({'file': filepath.replace('\\', '/'), 'line': i, 'type': kw.strip()})
                            count += 1
                            break
        except:
            pass

print(f'Found {count} critical stubs')

with open('STUB_INVENTORY.json', 'w') as f:
    json.dump({'total': count, 'stubs': stubs}, f, indent=2)

print('Saved to STUB_INVENTORY.json')
