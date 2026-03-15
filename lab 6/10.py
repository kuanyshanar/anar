n = int(input())
arr = list(map(int, input().split()))

count = sum(map(lambda x: bool(x), arr))
print(count)