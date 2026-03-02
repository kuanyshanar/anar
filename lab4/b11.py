import json

def apply_patch(s, p):
    for key, value in p.items():
        if value is None:
            s.pop(key, None)
        elif key in s and isinstance(s[key], dict) and isinstance(value, dict):
            apply_patch(s[key], value)
        else:
            s[key] = value
    return s


s = json.loads(input())
p= json.loads(input())

result = apply_patch(s, p)

print(json.dumps(result, separators=(',', ':'), sort_keys=True))