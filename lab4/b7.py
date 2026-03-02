#soz keri
def func(a):
    for i in a[::-1]:
        yield i

n = input()

for b in func(n):
    print(b, end="")