import time
import csv
from src.utils.time_utils import _is_past_timestamp, _is_unix_millisecond_timestamp
from src.core.validator import Validator

class VoucherValidator(Validator):
    voucher_columns = ['userId', 'externalId', 'voucherType', 'voucherName', 'iconName', 'code', 'expiration']

    def __init__(self, csv_path, log_path, expected_columns=voucher_columns):
        super().__init__(csv_path=csv_path, log_path=log_path, expected_columns=expected_columns)
        self.default_icon = "basket-colors-1"

    def _validate_row(self, values):
        errors = []
        if len(values) != len(self.expected_columns):
            errors.append(f"Row should have {len(self.expected_columns)} columns")

        if not values[0] and not values[1]:
            errors.append("Column 'userId' and 'externalId' should not be empty at the same time")
        if values[2] not in ["one_time", "yearly"]:
            errors.append("Column 'voucherType' should be either 'one_time' or 'yearly'")
        if not values[3]:
            errors.append("Column 'voucherName' should not be empty")
        if not values[4]:
            errors.append("Column 'iconName' should not be empty")
        if not values[5]:
            errors.append("Column 'code' should not be empty")
        try:
            expiration = int(values[6])
            valid, message = _is_unix_millisecond_timestamp(expiration)
            if not valid:
                errors.append(message)
            past, message = _is_past_timestamp(expiration)
            if past:
                errors.append(message)
        except ValueError:
            errors.append("Column 'expiration' should be an integer (UNIX timestamp in milliseconds)")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, ""