n = int(input())
arr = list(map(str, input().split()))

for i, j in enumerate(arr):
    print(str(i) + ":" + j, end=" ")