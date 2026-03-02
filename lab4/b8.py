#jai san
def primes(n):
    for x in range(2, n+1):
        if all(x % i != 0 for i in range(2, int(x**0.5)+1)):
            yield x

print(*primes(int(input())))