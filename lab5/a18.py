import re
a=input()
b=input()
pattern=re.escape(b)
print(len(re.findall(pattern,a)))

