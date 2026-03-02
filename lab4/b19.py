import math
import sys

EPS = 1e-12
PI2 = 2.0 * math.pi

def dist(x, y):
    return math.hypot(x, y)

def min_angle(a):
    """приводит угол к [-pi, pi]"""
    a = (a + math.pi) % (2.0 * math.pi) - math.pi
    return a

def segment_min_dist2_to_origin(ax, ay, bx, by):
    dx = bx - ax
    dy = by - ay
    dd = dx*dx + dy*dy
    if dd < EPS:
        return ax*ax + ay*ay

    t = -(ax*dx + ay*dy) / dd
    if t < 0.0:
        cx, cy = ax, ay
    elif t > 1.0:
        cx, cy = bx, by
    else:
        cx, cy = ax + t*dx, ay + t*dy
    return cx*cx + cy*cy

R = float(sys.stdin.readline().strip())
ax, ay = map(float, sys.stdin.readline().split())
bx, by = map(float, sys.stdin.readline().split())

ab = dist(bx - ax, by - ay)

min_d2 = segment_min_dist2_to_origin(ax, ay, bx, by)
if min_d2 >= R*R - EPS:
    print(f"{ab:.10f}")
    sys.exit(0)

da = dist(ax, ay)
db = dist(bx, by)

da = max(da, R)
db = max(db, R)

tang_a = math.sqrt(max(0.0, da*da - R*R))
tang_b = math.sqrt(max(0.0, db*db - R*R))

ang_a = math.atan2(ay, ax)
ang_b = math.atan2(by, bx)

gamma_a = math.acos(min(1.0, max(-1.0, R / da)))
gamma_b = math.acos(min(1.0, max(-1.0, R / db)))

best = float('inf')

for sa in (-1.0, 1.0):
    ta = ang_a + sa * gamma_a
    for sb in (-1.0, 1.0):
        tb = ang_b + sb * gamma_b
        dtheta = abs(min_angle(ta - tb)) 
        cand = tang_a + tang_b + R * dtheta
        if cand < best:
            best = cand

print(f"{best:.10f}")