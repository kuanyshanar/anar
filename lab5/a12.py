import re
a=input()
print(*re.findall(r"[0-9]{2,}", a))
