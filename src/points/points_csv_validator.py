import time
from src.utils.time_utils import _is_past_timestamp, _is_unix_millisecond_timestamp
from src.core.validator import Validator

class PointsValidator(Validator):
    points_columns = ["userId", "pointsToSpend", "statusPoints", "cashback", "allocatedAt", "expireAt", "setPlanExpiration", "reason", "title", "description"]

    def __init__(self, csv_path, expected_columns=points_columns):
        super(self, csv_path, expected_columns)

    def _validate_row(self, values):
        if len(values) != len(self.expected_columns):
            return False, f"Row should have {len(self.expected_columns)} columns"

        # Extract the required values
        points_to_spend, status_points, cashback = values[1], values[2], values[3]
        
        # Check if at least one of the values is valid and positive
        valid_pts = (points_to_spend.isdigit() and int(points_to_spend) > 0)
        valid_status = (status_points.isdigit() and int(status_points) > 0)
        try:
            valid_cashback = (float(cashback) >= 0)
        except ValueError:
            valid_cashback = False

        if not (valid_pts or valid_status or valid_cashback):
            return False, "At least one of 'pointsToSpend', 'statusPoints', or 'cashback' must have a valid positive value."

        # Ensure no negative values
        if (points_to_spend and int(points_to_spend) < 0) or (status_points and int(status_points) < 0) or (valid_cashback and float(cashback) < 0):
            return False, "Negative values are not allowed."
        
        # Ensure correct data types
        if points_to_spend and not points_to_spend.isdigit():
            return False, "Column 'pointsToSpend' should be an integer."
        if status_points and not status_points.isdigit():
            return False, "Column 'statusPoints' should be an integer."
        if cashback:
            try:
                float(cashback)
            except ValueError:
                return False, "Column 'cashback' should be a float."


        # Validate expireAt and setPlanExpiration
        if values[6].lower() == "true":
            if values[5]:  # If there's a value in expireAt
                return False, f"If setPlanExpiration is TRUE, expireAt should be empty"
        elif values[6].lower() == "false":
            try:
                expiration = int(values[5])
                valid, error_message = _is_unix_millisecond_timestamp(expiration)
                if not valid:
                    return False, error_message
                past, error_message = _is_past_timestamp(expiration)
                if past:
                    return False, f"expireAt should be a future UNIX timestamp in milliseconds when setPlanExpiration is FALSE"
            except ValueError:
                return False, f"expireAt should be an integer (UNIX timestamp in milliseconds) when setPlanExpiration is FALSE"
        else:
            return False, f"setPlanExpiration should be either TRUE or FALSE"

        return True, ""