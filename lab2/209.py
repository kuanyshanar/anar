n=int(input())
arr=list(map(int,input().split()))
maxx=max(arr)
minn=min(arr)
for i in range(n):
    if arr[i]==maxx:
        arr[i]=minn
print(*arr)
