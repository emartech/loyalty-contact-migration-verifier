import time
from src.utils.time_utils import _is_past_timestamp, _is_unix_millisecond_timestamp
from src.core.validator import Validator

class PointsValidator(Validator):
    points_columns = ["userId", "pointsToSpend", "statusPoints", "cashback", "allocatedAt", "expireAt", "setPlanExpiration", "reason", "title", "description"]

    def __init__(self, csv_path, log_path, expected_columns=points_columns):
        super().__init__(csv_path=csv_path, log_path=log_path, expected_columns=expected_columns)

    def _validate_row(self, values):
        errors = []
        if len(values) != len(self.expected_columns):
            errors.append(f"Row should have {len(self.expected_columns)} columns")

        # Extract the required values
        points_to_spend, status_points, cashback = values[1], values[2], values[3]

        # Ensure correct data types
        if points_to_spend and not points_to_spend.isdigit():
            errors.append("Column 'pointsToSpend' should be an integer.")
        if status_points and not status_points.isdigit():
            errors.append("Column 'statusPoints' should be an integer.")
        if cashback:
            try:
                float(cashback)
            except ValueError:
                errors.append("Column 'cashback' should be a float.")

        # None of the points columns contain invalid data types
        if not errors:
            # Check if at least one of the values is valid and positive
            valid_pts = (points_to_spend.isdigit() and int(points_to_spend) > 0)
            valid_status = (status_points.isdigit() and int(status_points) > 0)
            try:
                valid_cashback = (float(cashback) >= 0)
            except ValueError:
                valid_cashback = False

            if not (valid_pts or valid_status or valid_cashback):
                errors.append("At least one of 'pointsToSpend', 'statusPoints', or 'cashback' must have a valid positive value.")
            
            # Ensure no negative values
            if (points_to_spend and int(points_to_spend) < 0) or (status_points and int(status_points) < 0) or (valid_cashback and float(cashback) < 0):
                errors.append("Negative values are not allowed.")
        

        # Validate expireAt and setPlanExpiration
        if values[6].lower() == "true":
            if values[5]:  # If there's a value in expireAt
                errors.append("If setPlanExpiration is TRUE, expireAt should be empty")
        elif values[6].lower() == "false":
            try:
                expiration = int(values[5])
                valid, message = _is_unix_millisecond_timestamp(expiration)
                if not valid:
                    errors.append(message)
                past, message = _is_past_timestamp(expiration)
                if past:
                    errors.append("expireAt should be a future UNIX timestamp in milliseconds when setPlanExpiration is FALSE")
            except ValueError:
                errors.append("expireAt should be an integer (UNIX timestamp in milliseconds) when setPlanExpiration is FALSE")
        else:
            errors.append("setPlanExpiration should be either TRUE or FALSE")

        if errors:
            return False, "; ".join(errors)
        
        return True, ""