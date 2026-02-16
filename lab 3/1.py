def func(a):
    s = 0
    for i in range(len(a)):
        b = int(a[i])
        if b % 2 != 0:
            s += 1
    if s > 0:
        return "Not valid"
    else:
        return "Valid"
n = input()
print(func(n))