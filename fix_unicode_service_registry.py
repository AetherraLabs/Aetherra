import re

# Read the service registry file
with open('aetherra_service_registry.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Unicode characters with ASCII equivalents
replacements = [
    ('[WARN]', '[WARN]'),
    ('[OK]', '[OK]'),
    ('[ERROR]', '[ERROR]'),
    ('[DISC]', '[DISC]'),
    ('[TOOL]', '[TOOL]'),
    ('[FAIL]', '[FAIL]'),
    ('🔌', '[PLUGIN]'),
    ('🎙️', '[VOICE]'),
    ('🔗', '[LINK]')
]

for old, new in replacements:
    content = content.replace(old, new)

# Write back to file
with open('aetherra_service_registry.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Unicode characters replaced in service registry")
