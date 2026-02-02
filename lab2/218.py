a = int(input())
b = {} 

for i in range(1, a + 1):
    s = input().strip()
    if s not in b:
        b[s] = i

for s in sorted(b):
    print(s, b[s])