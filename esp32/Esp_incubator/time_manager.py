import ntptime
import time

# ==========================================
# Time Manager
# ==========================================

def sync_time():

    try:

        print("Synchronizing time...")

        ntptime.settime()

        print("Time synchronized.")

        return True

    except Exception as e:

        print("Time Sync Failed:", e)

        return False


def get_time():

    now = time.localtime()

    return {
        "year": now[0],
        "month": now[1],
        "day": now[2],
        "hour": now[3],
        "minute": now[4],
        "second": now[5]
    }


def is_within_schedule(start_hour,
                       start_minute,
                       end_hour,
                       end_minute):

    now = time.localtime()

    current = now[3] * 60 + now[4]

    start = start_hour * 60 + start_minute

    end = end_hour * 60 + end_minute

    return start <= current < end
