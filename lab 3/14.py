n = int(input())
arr = list(map(int, input().split()))
q = int(input())

for _ in range(q):
    op = input().split()

    if op[0] == "add":
        x = int(op[1])
        arr = list(map(lambda a: a + x, arr))

    elif op[0] == "multiply":
        x = int(op[1])
        arr = list(map(lambda a: a * x, arr))

    elif op[0] == "power":
        x = int(op[1])
        arr = list(map(lambda a: a ** x, arr))

    elif op[0] == "abs":
        arr = list(map(lambda a: abs(a), arr))

print(*arr)