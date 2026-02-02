n = int(input())
a = list(map(int, input().split()))
max = a[0]
ii = 1
for i in range(1, n):
    if a[i] > max:
        max = a[i]
        ii = i + 1
print(ii)