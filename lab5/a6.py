import re
a = input()
b = a.split()
for i in b[1]:
    if re.search("@", i):
        print(i)
    else: 
        print("No email")