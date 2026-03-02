import json

def tokenize(query: str):
    tokens = []
    i = 0
    n = len(query)

    while i < n:
        ch = query[i]

        if ch == '.':
            i += 1
            continue

        if ch == '[':
            j = i + 1
            if j >= n:
                return None

            k = j
            if k < n and query[k] == '-':  
                k += 1
            while k < n and query[k].isdigit():
                k += 1
            if k == j or k >= n or query[k] != ']':
                return None
            idx = int(query[j:k])
            tokens.append(("idx", idx))
            i = k + 1
            continue

        j = i
        while j < n and query[j] not in '.[':
            j += 1
        key = query[i:j]
        if key == "":
            return None
        tokens.append(("key", key))
        i = j

    return tokens


def resolve(root, query: str):
    tokens = tokenize(query)
    if tokens is None:
        return None, False

    cur = root
    for kind, val in tokens:
        if kind == "key":
            if not isinstance(cur, dict) or val not in cur:
                return None, False
            cur = cur[val]
        else:  # idx
            if not isinstance(cur, list):
                return None, False
            if val < 0 or val >= len(cur):
                return None, False
            cur = cur[val]

    return cur, True


data = json.loads(input())
q = int(input())

for _ in range(q):
    query = input().strip()
    value, ok = resolve(data, query)
    if not ok:
        print("NOT_FOUND")
    else:
        print(json.dumps(value, separators=(',', ':'), sort_keys=True))