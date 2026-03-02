import sys

x1, y1 = map(float, sys.stdin.readline().split())
x2, y2 = map(float, sys.stdin.readline().split())

x2_ref = x2
y2_ref = -y2

t = -y1 / (y2_ref - y1)

x_ref = x1 + t * (x2_ref - x1)
y_ref = 0.0

print(f"{x_ref:.10f} {y_ref:.10f}")