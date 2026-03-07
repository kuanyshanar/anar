import re
a=input()
words=re.findall(r"\b[A-Za-z]{3}\b",a)
print(len(words))