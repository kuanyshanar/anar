a = int(input())
b = {}
d = 0
for i in range(a):
    s = input().strip()
    if s in b:
        b[s] += 1
    else:
        b[s] = 1
for x in b:
    if b[x] == 3:
        d += 1
print(d)