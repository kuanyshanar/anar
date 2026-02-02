a = int(input())
c = 0
for i in range(1, a):
    if a % i == 0:
        c += 1
if c <= 2:
    print("YES")
else:
    print("NO")