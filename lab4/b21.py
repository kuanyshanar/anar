import sys
import importlib

q = int(sys.stdin.readline().strip())

for _ in range(q):
    line = sys.stdin.readline().strip()
    if not line:
        print("MODULE_NOT_FOUND")
        continue

    module_path, attr_name = line.split()

    try:
        module = importlib.import_module(module_path)
    except Exception:
        print("MODULE_NOT_FOUND")
        continue

    if not hasattr(module, attr_name):
        print("ATTRIBUTE_NOT_FOUND")
        continue

    attr = getattr(module, attr_name)
    print("CALLABLE" if callable(attr) else "VALUE")