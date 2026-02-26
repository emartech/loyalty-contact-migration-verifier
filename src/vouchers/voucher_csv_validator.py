# SPDX-FileCopyrightText: 2024 SAP Emarsys
# SPDX-License-Identifier: MIT

import time
import csv
from src.utils.time_utils import _is_past_timestamp, _is_unix_millisecond_timestamp, _has_decimal_separators, _needs_csv_quoting
from src.core.validator import Validator

class VoucherValidator(Validator):
    voucher_columns = ['userId', 'externalId', 'voucherType', 'voucherName', 'iconName', 'code', 'expiration']

    def __init__(self, csv_path, log_path, expected_columns=voucher_columns, delimiter=','):
        super().__init__(csv_path=csv_path, log_path=log_path, expected_columns=expected_columns, delimiter=delimiter)
        self.default_icon = "basket-colors-1"

    def _validate_row(self, values):
        errors = []
        timestamp_errors = []
        if len(values) != len(self.expected_columns):
            if len(values) > len(self.expected_columns):
                errors.append(f"Row has {len(values)} columns but should have {len(self.expected_columns)}. This often indicates unquoted commas in text fields. Fields containing commas must be enclosed in double quotes.")
            else:
                errors.append(f"Row should have {len(self.expected_columns)} columns")

        if len(values) > 1 and not values[0] and not values[1]:
            errors.append("Column 'userId' and 'externalId' should not be empty at the same time")
        if len(values) > 2 and values[2] not in ["one_time", "yearly"]:
            errors.append("Column 'voucherType' should be either 'one_time' or 'yearly'")
        if len(values) > 3 and not values[3]:
            errors.append("Column 'voucherName' should not be empty")
        elif len(values) > 3:
            needs_quoting, quoting_message = _needs_csv_quoting(values[3])
            if needs_quoting:
                errors.append(f"Column 'voucherName': {quoting_message}")
        if len(values) > 4 and not values[4]:
            errors.append("Column 'iconName' should not be empty")
        if len(values) > 5 and not values[5]:
            errors.append("Column 'code' should not be empty")
        if len(values) > 6:
            has_decimal, decimal_message = _has_decimal_separators(values[6])
            if has_decimal:
                timestamp_errors.append(f"Column 'expiration': {decimal_message}")
            else:
                try:
                    expiration = int(values[6])
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
                            errors.append(message)
                except ValueError:
                    errors.append("Column 'expiration' should be an integer (UNIX timestamp in milliseconds)")
        
        temp_timestamp_errors = getattr(self, '_temp_timestamp_errors', [])
        if hasattr(self, '_temp_timestamp_errors'):
            delattr(self, '_temp_timestamp_errors')
        
        all_timestamp_errors = timestamp_errors + temp_timestamp_errors
        all_errors = errors + all_timestamp_errors
        if all_errors:
            return False, "; ".join(all_errors), all_timestamp_errors
        
        return True, "", []