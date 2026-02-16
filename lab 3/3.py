s = input().strip()

to_digit = {
    "ZER": "0", "ONE": "1", "TWO": "2", "THR": "3", "FOU": "4",
    "FIV": "5", "SIX": "6", "SEV": "7", "EIG": "8", "NIN": "9"
}

to_word = {v: k for k, v in to_digit.items()}

for op in ['+', '-', '*']:
    if op in s:
        left, right = s.split(op)
        operation = op
        break

def word_to_number(w):
    return int("".join(to_digit[w[i:i+3]] for i in range(0, len(w), 3)))

a = word_to_number(left)
b = word_to_number(right)


if operation == '+':
    result = a + b
elif operation == '-':
    result = a - b
else:
    result = a * b


answer = "".join(to_word[d] for d in str(result))
print(answer)