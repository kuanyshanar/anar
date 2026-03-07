import re
a = input()
c = input()
b = re.split(c, a)
for i in range(len(b)):
    if i == len(b) - 1:
        print(b[i])
    else:
        print(b[i], end=",")