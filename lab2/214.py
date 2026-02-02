a = int(input())
b = list(map(int, input().split()))
s = {}
for i in b:
    if i in s:
        s[i] += 1
    else:
        s[i] = 1
maxx = 0
d = b[0]
for i in b:
    if s[i] > maxx:
        maxx = s[i]
        d = i
    elif s[i] == maxx and i < d:
        d = i
print(d)