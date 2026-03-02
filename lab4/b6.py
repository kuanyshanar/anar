#Fibonacci
def func(x):
    a, b = 0, 1
    for i in range(x):
        yield a
        a, b = b, a + b

n = int(input())

print(','.join(str(i) for i in func(n)))