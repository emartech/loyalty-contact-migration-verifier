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
        if len(values) != len(self.expected_columns):
            return False, f"Row should have {len(self.expected_columns)} columns"
        if values[2] not in ["one_time", "yearly"]:
            return False, "Column 'voucherType' should be either 'one_time' or 'yearly'"
        if not values[3]:
            return False, "Column 'voucherName' should not be empty"
        if not values[4]:
            return False, "Column 'iconName' should not be empty"
        if not values[5]:
            return False, "Column 'code' should not be empty"
        try:
            expiration = int(values[6])
            valid, error_message = _is_unix_millisecond_timestamp(expiration)
            if not valid:
                return False, error_message
            past, error_message = _is_past_timestamp(expiration)
            if past:
                return False, error_message
        except ValueError:
            return False, "Column 'expiration' should be an integer (UNIX timestamp in milliseconds)"
        return True, ""