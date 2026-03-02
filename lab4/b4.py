# a dan b kvadrattay
def func(a):
    for i in range(a[0], a[1] + 1):
        yield i ** 2

n = list(map(int,input().split()))

for b in func(n):
    print(b)

