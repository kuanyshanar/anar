#jyp san
def func(a):
    for i in range(a + 1):
        if i % 2 == 0:
            yield i

n = int(input())

for b in func(n):
    if b == n or b == n - 1: 
        print(b)
    else:
        print(b, end=",")
