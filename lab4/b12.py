import json

MISSING = "<missing>"
differences = []


def serialize(val):
    if val == MISSING:
        return MISSING
    return json.dumps(val, separators=(',', ':'), sort_keys=True)


def deep_diff(o1, o2, path=""):

    if isinstance(o1, dict) and isinstance(o2, dict):
        keys = sorted(set(o1.keys()) | set(o2.keys())) 
        for key in keys:
            new_path = f"{path}.{key}" if path else key

            v1 = o1.get(key, MISSING)
            v2 = o2.get(key, MISSING)

            if isinstance(v1, dict) and isinstance(v2, dict):
                deep_diff(v1, v2, new_path)
            elif v1 != v2:
                differences.append(f"{new_path} : {serialize(v1)} -> {serialize(v2)}")
        return

    if o1 != o2:
        differences.append(f"{path if path else '$'} : {serialize(o1)} -> {serialize(o2)}")


obj1 = json.loads(input())
obj2 = json.loads(input())

deep_diff(obj1, obj2)

if differences:
    for diff in sorted(differences):
        print(diff)
else:
    print("No differences")