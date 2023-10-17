import time

def _is_unix_millisecond_timestamp(timestamp_millis):
    # If it's too short to be a millisecond timestamp, reject it
    if abs(timestamp_millis) < 1e11:  # 10^11
        return False
    return True

def _is_past_timestamp(timestamp_millis):
    # Get current time in milliseconds
    current_time_millis = int(time.time() * 1000)
    return timestamp_millis < current_time_millis
