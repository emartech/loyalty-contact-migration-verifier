# SPDX-FileCopyrightText: 2024 SAP Emarsys
# SPDX-License-Identifier: MIT

import time
from src.utils.time_utils import _is_past_timestamp, _is_unix_millisecond_timestamp, _has_decimal_separators, _needs_csv_quoting
from src.core.validator import Validator

class PointsValidator(Validator):
    points_columns = ["userId", "pointsToSpend", "statusPoints", "cashback", "allocatedAt", "expireAt", "setPlanExpiration", "reason", "title", "description"]

    def __init__(self, csv_path, log_path, expected_columns=points_columns, delimiter=','):
        super().__init__(csv_path=csv_path, log_path=log_path, expected_columns=expected_columns, delimiter=delimiter)

    def _validate_row(self, values):
        errors = []
        if len(values) != len(self.expected_columns):
            if len(values) > len(self.expected_columns):
                errors.append(f"Row has {len(values)} columns but should have {len(self.expected_columns)}. This often indicates unquoted commas in text fields. Fields containing commas must be enclosed in double quotes.")
            else:
                errors.append(f"Row should have {len(self.expected_columns)} columns")

        points_to_spend, status_points, cashback = values[1], values[2], values[3]

        if points_to_spend:
            has_decimal, decimal_message = _has_decimal_separators(points_to_spend)
            if has_decimal:
                errors.append(f"Column 'pointsToSpend': {decimal_message}")
            elif not points_to_spend.isdigit():
                errors.append("Column 'pointsToSpend' should be an integer.")
        
        if status_points:
            has_decimal, decimal_message = _has_decimal_separators(status_points)
            if has_decimal:
                errors.append(f"Column 'statusPoints': {decimal_message}")
            elif not status_points.isdigit():
                errors.append("Column 'statusPoints' should be an integer.")
        
        if cashback:
            has_decimal, decimal_message = _has_decimal_separators(cashback)
            if has_decimal:
                errors.append(f"Column 'cashback': {decimal_message}")
            else:
                try:
                    float(cashback)
                except ValueError:
                    errors.append("Column 'cashback' should be a float.")

        if not errors:
            valid_pts = (points_to_spend.isdigit() and int(points_to_spend) > 0)
            valid_status = (status_points.isdigit() and int(status_points) > 0)
            try:
                valid_cashback = (cashback and float(cashback) > 0)
            except ValueError:
                valid_cashback = False

            if not (valid_pts or valid_status or valid_cashback):
                errors.append("At least one of 'pointsToSpend', 'statusPoints', or 'cashback' must have a valid positive value.")
            
            if (points_to_spend and int(points_to_spend) < 0) or (status_points and int(status_points) < 0) or (valid_cashback and float(cashback) < 0):
                errors.append("Negative values are not allowed.")
        
        for i, field_name in enumerate(['reason', 'title', 'description']):
            field_index = 7 + i
            if field_index < len(values) and values[field_index]:
                needs_quoting, quoting_message = _needs_csv_quoting(values[field_index])
                if needs_quoting:
                    errors.append(f"Column '{field_name}': {quoting_message}")

        if len(values) > 4 and values[4]:
            errors.append("Column 'allocatedAt' must be empty")

        if len(values) > 9 and values[9] and (len(values) <= 8 or not values[8]):  
            errors.append("Column 'description' requires 'title' to be set")

        if len(values) > 6 and values[6].lower() == "true":
            if len(values) > 5 and values[5]:
                errors.append("If setPlanExpiration is TRUE, expireAt should be empty")
        elif len(values) > 6 and values[6].lower() == "false":
            if len(values) > 5:
                try:
                    expiration = int(values[5])
                    valid, message = _is_unix_millisecond_timestamp(expiration)
                    if not valid:
                        if "appears to be in seconds instead of milliseconds" in message:
                            timestamp_errors = getattr(self, '_temp_timestamp_errors', [])
                            timestamp_errors.append(message)
                            self._temp_timestamp_errors = timestamp_errors
                        else:
                            errors.append(message)
                    else:
                        past, message = _is_past_timestamp(expiration)
                        if past:
                            errors.append("expireAt should be a future UNIX timestamp in milliseconds when setPlanExpiration is FALSE")
                except ValueError:
                    errors.append("expireAt should be an integer (UNIX timestamp in milliseconds) when setPlanExpiration is FALSE")
        elif len(values) > 6:
            errors.append("setPlanExpiration should be either TRUE or FALSE")

        timestamp_errors = getattr(self, '_temp_timestamp_errors', [])
        if hasattr(self, '_temp_timestamp_errors'):
            delattr(self, '_temp_timestamp_errors')
        
        all_errors = errors
        if all_errors or timestamp_errors:
            return False, "; ".join(all_errors + timestamp_errors), timestamp_errors
        
        return True, "", []