import re
a=input()
b=re.compile(r"^\d+$")
if b.match(a):
    print("Match")
else:
    print("No match")
