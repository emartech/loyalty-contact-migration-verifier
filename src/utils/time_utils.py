import time

def _is_unix_millisecond_timestamp(timestamp):
    if isinstance(timestamp, int) and timestamp > 0:
        if timestamp < 1e9:  # Likely a Unix second timestamp (up to November 2001)
            return False, "Timestamp likely in seconds format."
        elif timestamp < 2e12:  # Reasonable range for a Unix millisecond timestamp (up to 2073)
            return True, "Timestamp is a valid Unix millisecond timestamp."
        else:
            return False, "Timestamp exceeds reasonable future date range."
    else:
        return False, "Timestamp is not a positive integer."

def _is_past_timestamp(timestamp_millis):
    # Get current time in milliseconds
    current_time_millis = int(time.time() * 1000)
    return timestamp_millis < current_time_millis
