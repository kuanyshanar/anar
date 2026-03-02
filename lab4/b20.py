import sys

g = 0
n = 0

m = int(sys.stdin.readline().strip())

for _ in range(m):
    scope, value = sys.stdin.readline().split()
    value = int(value)
    
    if scope == "global":
        g += value
    elif scope == "nonlocal":
        n += value
    
print(g, n)