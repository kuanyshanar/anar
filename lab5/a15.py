import re
a=input()
print(re.sub(r"\d", lambda m: m.group(0) * 2, a))
