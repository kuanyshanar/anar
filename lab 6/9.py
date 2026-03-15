n = int(input())
a = list(map(str, input().split()))
b = list(map(str, input().split()))
m = input()
for d, c in zip(a, b):
    if m == d:
        print(c)
        break
else:
    print("Not found")