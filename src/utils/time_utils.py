import time
from datetime import datetime

# Constants for the range of valid Unix timestamps
FROM_DATE = datetime(1970, 1, 2).timestamp() * 1000
TILL_DATE = datetime(2100, 1, 1).timestamp() * 1000

def _is_unix_millisecond_timestamp(timestamp):
    try:
        # Convert the timestamp to integer
        timestamp_int = int(timestamp)
        
        # Check if the timestamp is within the range
        if FROM_DATE <= timestamp_int <= TILL_DATE:
            return True, "Timestamp is a valid Unix millisecond timestamp between {} and {}.".format(FROM_DATE, TILL_DATE)
        else:
            return False, "Timestamp {{}) is a valid Unix millisecond timestamp, but it is outside of the range from {} till {}.".format(timestamp_int,FROM_DATE, TILL_DATE)
    except:
        return False, "Timestamp ({}) is not a valid Unix millisecond timestamp.".format(timestamp)

def _is_past_timestamp(timestamp_millis):
    # Get current time in milliseconds
    current_time_millis = int(time.time() * 1000)
    return timestamp_millis < current_time_millis, "Timestamp ({}) is in the past. Current timestamp: {}".format(timestamp_millis, current_time_millis)
