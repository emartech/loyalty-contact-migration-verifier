import time
import csv
from src.utils.time_utils import _is_past_timestamp, _is_unix_millisecond_timestamp
from src.core.validator import Validator

class VoucherValidator(Validator):
    voucher_columns = ['userId', 'externalId', 'voucherType', 'voucherName', 'iconName', 'code', 'expiration']

    def __init__(self, csv_path, expected_columns=voucher_columns):
        super().__init__(csv_path=csv_path, expected_columns=expected_columns)
        self.default_icon = "basket-colors-1"

    def _validate_row(self, values):
        errors = []
        if len(values) != len(self.expected_columns):
            error_message = f"Row should have {len(self.expected_columns)} columns"
            errors = errors + [error_message]
            # If there are not enough fields in the row there is no need for further validation
            return False, errors

        if not values[0] and not values[1]:
            error_message = "Column 'userId' and 'externalId' should not be empty at the same time"
            errors = errors + [error_message]
        if values[2] not in ["one_time", "yearly"]:
            error_message = "Column 'voucherType' should be either 'one_time' or 'yearly'"
            errors = errors + [error_message]
        if not values[3]:
            error_message = "Column 'voucherName' should not be empty"
            errors = errors + [error_message]
        if not values[4]:
            error_message = "Column 'iconName' should not be empty"
            errors = errors + [error_message]
        if not values[5]:
            error_message = "Column 'code' should not be empty"
            errors = errors + [error_message]
        try:
            expiration = int(values[6])
            valid, error_message = _is_unix_millisecond_timestamp(expiration)
            if not valid:
                errors = errors + [error_message]
            past, error_message = _is_past_timestamp(expiration)
            if past:
                errors = errors + [error_message]
        except ValueError:
            error_message = "Column 'expiration' should be an integer (UNIX timestamp in milliseconds)"
            errors = errors + [error_message]
        if len(errors) > 0:
            return False, errors
        return True, ""