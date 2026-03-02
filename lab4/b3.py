#3 and 4ke boly
def func(a):
    for i in range(a + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

n = int(input())

for b in func(n):
    print(b, end=" ")