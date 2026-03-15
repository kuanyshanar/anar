n = int(input())
A = list(map(int, input().split()))
B = list(map(int, input().split()))
product = 0
for a, b in zip(A, B):
    product += a * b
print(product)