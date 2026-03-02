from datetime import datetime, timedelta
import sys

SECONDS_IN_DAY = 86400

def is_leap(year: int) -> bool:
    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)

def parse_line(line: str):
    date_part, tz_part = line.strip().split()
    dt_local_mid = datetime.strptime(date_part, "%Y-%m-%d")

    sign = 1 if tz_part[3] == '+' else -1
    hh = int(tz_part[4:6])
    mm = int(tz_part[7:9])
    offset = timedelta(hours=hh, minutes=mm) * sign

    return dt_local_mid, offset

def birthday_local_for_year(year: int, month: int, day: int) -> datetime:
    if month == 2 and day == 29 and not is_leap(year):
        return datetime(year, 2, 28)
    return datetime(year, month, day)

birth_line = sys.stdin.readline().strip()
curr_line = sys.stdin.readline().strip()

birth_dt_local, birth_offset = parse_line(birth_line)
curr_dt_local, curr_offset = parse_line(curr_line)

birth_month = birth_dt_local.month
birth_day = birth_dt_local.day

curr_utc = curr_dt_local - curr_offset

curr_in_birth_tz = curr_utc + birth_offset
year = curr_in_birth_tz.year


bday_local = birthday_local_for_year(year, birth_month, birth_day)
bday_utc = bday_local - birth_offset

if bday_utc < curr_utc:
    year += 1
    bday_local = birthday_local_for_year(year, birth_month, birth_day)
    bday_utc = bday_local - birth_offset

delta_seconds = (bday_utc - curr_utc).total_seconds()

if delta_seconds <= 0:
    print(0)
else:
    days_left = int((delta_seconds + SECONDS_IN_DAY - 1) // SECONDS_IN_DAY)
    print(days_left)