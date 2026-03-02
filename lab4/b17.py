import math
import sys

def inside_circle(x, y, R):
    return x*x + y*y <= R*R + 1e-12

R = float(sys.stdin.readline().strip())
ax, ay = map(float, sys.stdin.readline().split())
bx, by = map(float, sys.stdin.readline().split())

dx = bx - ax
dy = by - ay

seg_len = math.hypot(dx, dy)
if seg_len == 0.0:
    print("0.0000000000")
    sys.exit(0)

a = dx*dx + dy*dy
b = 2.0 * (ax*dx + ay*dy)
c = ax*ax + ay*ay - R*R

disc = b*b - 4*a*c

if disc < 0:

    if inside_circle(ax, ay, R) and inside_circle(bx, by, R):
        ans = seg_len
    else:
        ans = 0.0
else:
    sqrt_disc = math.sqrt(max(0.0, disc))
    t1 = (-b - sqrt_disc) / (2*a)
    t2 = (-b + sqrt_disc) / (2*a)
    if t1 > t2:
        t1, t2 = t2, t1

    left = max(0.0, t1)
    right = min(1.0, t2)

    if right <= left:
        ans = 0.0
    else:
        ans = (right - left) * seg_len

print(f"{ans:.10f}")