n, l, r = map(int,input().split())
a = list(map(int,input().split()))
l -= 1
r -= 1
while l < r:
    a[l],a[r] = a[r],a[l]
    l += 1
    r -= 1
print(*a)
