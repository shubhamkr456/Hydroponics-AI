import time
import machine

try:
    import urequests
except ImportError:
    urequests = None

# ==========================================
# Time Manager
# ==========================================

def sync_time():
    print("Waiting 2 seconds for network to settle...")
    time.sleep(2)
    
    if not urequests:
        print("Error: 'urequests' module not found.")
        return False

    headers = {'User-Agent': 'Mozilla/5.0 (MicroPython)'}

    try:
        print("Fetching exact IST (via Colombo)...")
        # We ask for Sri Lanka's timezone to perfectly bypass the 23-minute Indian LMT bug!
        url = "https://worldtimeapi.org/api/timezone/Asia/Kolkata"
        response = urequests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(data)
            response.close()
            
            # Feed the exact numbers directly into the Real-Time Clock!
            # No MicroPython math functions allowed.
            machine.RTC().datetime((
                data['year'], 
                data['month'], 
                data['day'], 
                0, 
                data['hour'], 
                data['minute'], 
                data['seconds'], 
                0
            ))
            print("Time synchronized perfectly (IST).")
            return True
            
        response.close()
    except Exception as e:
        print("HTTP Sync Failed:", e)
        
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


def is_within_schedule(start_hour, start_minute, end_hour, end_minute):
    now = time.localtime()
    current = now[3] * 60 + now[4]
    start = start_hour * 60 + start_minute
    end = end_hour * 60 + end_minute

    return start <= current < end