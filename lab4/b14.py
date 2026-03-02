from datetime import datetime, timedelta
import sys

def parse_moment(s: str) -> datetime:
    s = s.strip()
    date_part, tz_part = s.split() 


    local_mid = datetime.strptime(date_part, "%Y-%m-%d")

    sign = 1 if tz_part[3] == '+' else -1
    hh = int(tz_part[4:6])
    mm = int(tz_part[7:9])

    offset = timedelta(hours=hh, minutes=mm) * sign

    return local_mid - offset

s1 = sys.stdin.readline().strip()
s2 = sys.stdin.readline().strip()

t1 = parse_moment(s1)
t2 = parse_moment(s2)

diff_seconds = abs((t1 - t2).total_seconds())
print(int(diff_seconds // 86400))