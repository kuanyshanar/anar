a=int(input())
s={}
for i in range(a):
    n,k=input().split( )
    k=int(k)
    if n in s:
        s[n]+=k
    else:
        s[n]=k
for c in sorted(s):
    print(c,s[c])