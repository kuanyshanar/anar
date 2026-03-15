n = int(input())
arr = list(map(str, input().split()))

print(max(arr, key=len))