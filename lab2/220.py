import sys
input = sys.stdin.readline
n = int(input())
db = {}
out = []

for _ in range(n):
    line = input().rstrip('\n')

    if line.startswith("set"):
        parts = line.split(maxsplit=2)
        key = parts[1]
        value = parts[2] if len(parts) == 3 else ""
        db[key] = value

    else:  # get
        key = line.split()[1]
        if key in db:
            out.append(db[key])
        else:
            out.append(f"KE: no key {key} found in the document")

sys.stdout.write("\n".join(out))
