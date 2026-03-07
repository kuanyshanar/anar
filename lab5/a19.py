import re
a=input()
word_re = re.compile(r"\b\w+\b")
print(len(word_re.findall(a)))