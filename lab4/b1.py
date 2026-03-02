#kvadrat
def func(a):
    for i in range(1, a + 1):
        yield i ** 2

n = int(input())

for b in func(n):
    print(b)

