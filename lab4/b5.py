#keri retpen shygaru
def func(a):
    for i in range(a, -1, -1):
        yield i

n = int(input())

for b in func(n):
    print(b)