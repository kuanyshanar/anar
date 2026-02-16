n = list(map(int, input().split()))
is_prime = lambda n: n > 1 and all(n % i != 0 for i in range(2, int(n**0.5) + 1))

prime = list(filter(is_prime, n))

if prime:
    print(*prime)
else:
    print("No primes")