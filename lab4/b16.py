from datetime import datetime, timedelta
import sys

def parse_moment(line: str) -> datetime:
    date_part, time_part, tz_part = line.strip().split()

    dt_local = datetime.strptime(
        f"{date_part} {time_part}",
        "%Y-%m-%d %H:%M:%S"
    )


    sign = 1 if tz_part[3] == '+' else -1
    hours = int(tz_part[4:6])
    minutes = int(tz_part[7:9])

    offset = timedelta(hours=hours, minutes=minutes) * sign

    return dt_local - offset


start_line = sys.stdin.readline().strip()
end_line = sys.stdin.readline().strip()

start_utc = parse_moment(start_line)
end_utc = parse_moment(end_line)

duration_seconds = int((end_utc - start_utc).total_seconds())

print(duration_seconds)