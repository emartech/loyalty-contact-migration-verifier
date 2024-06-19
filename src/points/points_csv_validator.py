import time
from src.utils.time_utils import _is_past_timestamp, _is_unix_millisecond_timestamp
from src.core.validator import Validator

class PointsValidator(Validator):
    points_columns = ["userId", "pointsToSpend", "statusPoints", "cashback", "allocatedAt", "expireAt", "setPlanExpiration", "reason", "title", "description"]

    def __init__(self, csv_path, expected_columns=points_columns):
        super().__init__(csv_path=csv_path, expected_columns=expected_columns)

    def _validate_row(self, values):
        errors = []
        if len(values) != len(self.expected_columns):
            error_message = f"Row should have {len(self.expected_columns)} columns"
            errors = errors + [error_message]
            # If there are not enough fields in the row there is no need for further validation
            return False, errors

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
            error_message = "At least one of 'pointsToSpend', 'statusPoints', or 'cashback' must have a valid positive value."
            errors = errors + [error_message]
            # If no Valid Points, Status or Cashback the rest of the line does not need to be checked
            return False, errors

        # Ensure no negative values
        if (points_to_spend and int(points_to_spend) < 0) or (status_points and int(status_points) < 0) or (valid_cashback and float(cashback) < 0):
            error_message = "Negative values are not allowed."
            errors = errors + [error_message]
        
        # Ensure correct data types
        if points_to_spend and not points_to_spend.isdigit():
            error_message = "Column 'pointsToSpend' should be an integer."
            errors = errors + [error_message]
        if status_points and not status_points.isdigit():
            error_message = "Column 'statusPoints' should be an integer."
            errors = errors + [error_message]
        if cashback:
            try:
                float(cashback)
            except ValueError:
                error_message = "Column 'cashback' should be a float."
                errors = errors + [error_message]


        # Validate expireAt and setPlanExpiration
        if values[6].lower() == "true":
            if values[5]:  # If there's a value in expireAt
                error_message = f"If setPlanExpiration is TRUE, expireAt should be empty"
                errors = errors + [error_message]
        elif values[6].lower() == "false":
            try:
                expiration = int(values[5])
                valid, error_message = _is_unix_millisecond_timestamp(expiration)
                if not valid:
                    errors = errors + [error_message]
                past, error_message = _is_past_timestamp(expiration)
                if past:
                    error_message = f"expireAt should be a future UNIX timestamp in milliseconds when setPlanExpiration is FALSE"
                    errors = errors + [error_message]
            except ValueError:
                error_message = f"expireAt should be an integer (UNIX timestamp in milliseconds) when setPlanExpiration is FALSE"
                errors = errors + [error_message]
        else:
            error_message = f"setPlanExpiration should be either TRUE or FALSE"
            errors = errors + [error_message]

        if len(errors) > 0:
            return False, errors
        
        return True, ""