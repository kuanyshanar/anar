#input 1 2  * 2
#output 1 2 1 2
def func(a):
    for i in range(k):
        for x in a:
            yield x

n = input().split()
k = int(input())


for b in func(n):
    print(b, end=" ")