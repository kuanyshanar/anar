n = int(input())
arr = list(map(int, input().split()))
count = 0
for i in arr:
    count += i ** 2
print(count)