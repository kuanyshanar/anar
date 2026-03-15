n = int(input())
arr = list(map(int, input().split()))
even = list(filter(lambda a: a % 2 == 0, arr))
count = 0
for i in even:
    count += 1

print(count)