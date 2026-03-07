import re

s = input()
if re.findall(r"(cat|dog)", s):
    print("Yes")
else:
    print("No")
