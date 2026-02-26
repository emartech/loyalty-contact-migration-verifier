import time
from datetime import datetime, timezone

# Use timezone-aware datetime to avoid Windows epoch issues
FROM_DATE = datetime(1970, 1, 2, tzinfo=timezone.utc).timestamp() * 1000
TILL_DATE = datetime(2100, 1, 1, tzinfo=timezone.utc).timestamp() * 1000

def _is_unix_millisecond_timestamp(timestamp):
    """
    Validates that a timestamp is in Unix milliseconds format only.
    Rejects all other Unix time formats (seconds, microseconds, nanoseconds, etc.)
    """
    if timestamp < 0:
        return False, "Timestamp ({}) cannot be a negative value. Unix timestamps must be positive milliseconds (13 digits).".format(timestamp)
    
    try:
        timestamp_int = int(timestamp)
        current_time_seconds = int(time.time())
        current_time_millis = current_time_seconds * 1000
        
        digit_count = len(str(timestamp_int))
        
        if 1 <= timestamp_int <= 999999999:
            if digit_count <= 6:
                return False, "Timestamp ({}) appears to be in minutes/hours format ({} digits). Unix timestamps must be in milliseconds (13 digits, e.g., {}).".format(timestamp_int, digit_count, current_time_millis)
            elif digit_count <= 9:
                return False, "Timestamp ({}) appears to be in days or other small unit format ({} digits). Unix timestamps must be in milliseconds (13 digits, e.g., {}).".format(timestamp_int, digit_count, current_time_millis)
        
        elif 1000000000 <= timestamp_int <= 99999999999:
            return False, "Timestamp ({}) appears to be in seconds format ({} digits). Unix timestamps must be in milliseconds (13 digits, e.g., {}).".format(timestamp_int, digit_count, current_time_millis)
        
        elif 100000000000 <= timestamp_int <= 999999999999:
            return False, "Timestamp ({}) is close but appears to be truncated milliseconds ({} digits). Unix timestamps must be exactly 13 digits in milliseconds (e.g., {}).".format(timestamp_int, digit_count, current_time_millis)
        
        elif 1000000000000 <= timestamp_int <= 9999999999999:
            if FROM_DATE <= timestamp_int <= TILL_DATE:
                return True, "Timestamp is a valid Unix millisecond timestamp.".format()
            else:
                return False, "Timestamp ({}) is in milliseconds format but outside valid date range (1970-2100). Valid range: {} to {}.".format(timestamp_int, int(FROM_DATE), int(TILL_DATE))
        
        elif 10000000000000 <= timestamp_int <= 999999999999999:
            return False, "Timestamp ({}) appears to have extra precision or be in microseconds format ({} digits). Unix timestamps must be exactly 13 digits in milliseconds (e.g., {}).".format(timestamp_int, digit_count, current_time_millis)
        
        elif timestamp_int >= 1000000000000000:
            if digit_count == 16:
                return False, "Timestamp ({}) appears to be in microseconds format ({} digits). Unix timestamps must be in milliseconds (13 digits, e.g., {}).".format(timestamp_int, digit_count, current_time_millis)
            elif digit_count >= 19:
                return False, "Timestamp ({}) appears to be in nanoseconds format ({} digits). Unix timestamps must be in milliseconds (13 digits, e.g., {}).".format(timestamp_int, digit_count, current_time_millis)
            else:
                return False, "Timestamp ({}) appears to be in high-precision format ({} digits). Unix timestamps must be in milliseconds (13 digits, e.g., {}).".format(timestamp_int, digit_count, current_time_millis)
        
        else:
            return False, "Timestamp ({}) format not recognized. Unix timestamps must be in milliseconds (13 digits, e.g., {}).".format(timestamp_int, current_time_millis)
            
    except ValueError:
        return False, "Timestamp ({}) is not a valid integer. Unix timestamps must be in milliseconds (13 digits).".format(timestamp)
    except Exception as e:
        return False, "Timestamp ({}) validation failed: {}. Unix timestamps must be in milliseconds (13 digits).".format(timestamp, str(e))

def _is_past_timestamp(timestamp_millis):
    current_time_millis = int(time.time() * 1000)
    return timestamp_millis < current_time_millis, "Timestamp ({}) is in the past. Current timestamp: {}".format(timestamp_millis, current_time_millis)

def _has_decimal_separators(value):
    """Check if a value contains decimal separators (comma or period) which shouldn't be in integer fields."""
    if not value:
        return False, ""
    
    if ',' in value and value.count(',') == 1 and value.split(',')[1].isdigit():
        return True, "Value contains comma as decimal separator. Integer fields should not have decimal values."
    
    if '.' in value and value.count('.') == 1 and value.split('.')[1].isdigit():
        return True, "Value contains decimal point. Integer fields should not have decimal values."
    
    return False, ""

def _needs_csv_quoting(value):
    """Check if a text value needs proper CSV quoting due to containing commas."""
    if not value:
        return False, ""
    
    if ',' in value:
        return True, "Text contains commas and should be enclosed in double quotes for proper CSV formatting."
    
    return False, ""
