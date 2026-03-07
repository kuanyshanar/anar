import re
a=input()
m = re.match(r"^Name:\s*(.+?),\s*Age:\s*(.+?)\s*$",a)
print(m.group(1), m.group(2))