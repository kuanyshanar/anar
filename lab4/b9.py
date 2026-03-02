#2 darezheleri
def func(a):
    for i in range(a + 1):
        yield 2**i

n = int(input())

for b in func(n):
    print(b, end=" ")

