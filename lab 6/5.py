s = input()
for i in s:
    if i in "AaEeIiOoUu":
        print("Yes")
        break
else:
    print("No")