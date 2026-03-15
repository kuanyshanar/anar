n = int(input())
arr = list(map(int, input().split()))
if all(x >= 0 for x in arr):
    print("Yes")
else:
    print("No")