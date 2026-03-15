n = int(input())
arr = list(map(int, input().split()))

a = sorted(set(arr))
print(*a)