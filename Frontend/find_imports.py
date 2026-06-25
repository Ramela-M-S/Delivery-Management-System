import os
import re

import_pattern = re.compile(r'from\s+["\']([^.\'"]\S*)["\']')

dependencies = set()

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith(('.ts', '.tsx')):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        match = import_pattern.search(line)
                        if match:
                            dep = match.group(1)
                            # Handle scoped packages like @radix-ui/react-slot
                            parts = dep.split('/')
                            if dep.startswith('@'):
                                dep_name = '/'.join(parts[:2])
                            else:
                                dep_name = parts[0]
                            dependencies.add(dep_name)
            except Exception as e:
                pass

print("Found dependencies:")
for dep in sorted(dependencies):
    print(f"  - {dep}")
