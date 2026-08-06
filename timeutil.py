# 时间校验与离线时间恢复
import machine
import time

import state


def days_in_month(y, m):
    if m == 2:
        if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0:
            return 29
        return 28
    if m in (4, 6, 9, 11):
        return 30
    return 31


def compute_weekday(y, m, d, hh, mm, ss):
    ts = time.mktime((y, m, d, hh, mm, ss, 0, 0))
    return time.localtime(ts)[6]


def restore_saved_time():
    try:
        with open(state.TIME_SAVE_FILE, 'r') as f:
            data = f.read().strip()
        parts = [int(x) for x in data.split(',')]
        if len(parts) != 6:
            return
        y, m, d, hh, mm, ss = parts
        if not (2000 <= y <= 2099 and 1 <= m <= 12 and 1 <= d <= 31):
            return
        if not (0 <= hh <= 23 and 0 <= mm <= 59 and 0 <= ss <= 59):
            return
        if d > days_in_month(y, m):
            d = days_in_month(y, m)
        wd = compute_weekday(y, m, d, hh, mm, ss)
        machine.RTC().datetime((y, m, d, wd, hh, mm, ss, 0))
    except Exception:
        pass
