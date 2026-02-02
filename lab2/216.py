a = int(input())
b = list(map(int,input().split()))
s = set()
for c in b:
    if c in s:
        print("NO")
    else:
        print("YES")
        s.add(c)