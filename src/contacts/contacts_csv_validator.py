# SPDX-FileCopyrightText: 2024 SAP Emarsys
# SPDX-License-Identifier: GPL-3.0-only

import time
from src.utils.time_utils import _is_past_timestamp, _is_unix_millisecond_timestamp
from src.core.validator import Validator

class ContactsValidator(Validator):
    contact_columns = ['userId', 'shouldJoin', 'joinDate', 'tierName', 'tierEntryAt', 'tierCalcAt', 'shouldReward']

    def __init__(self, csv_path, log_path, expected_columns=contact_columns, delimiter=','):
        super().__init__(csv_path=csv_path, log_path=log_path, expected_columns=expected_columns, delimiter=delimiter)
        self.seen_user_ids = set()

    def _validate_row(self, values):
        errors = []
        if len(values) != len(self.expected_columns):
            errors.append(f"Row should have {len(self.expected_columns)} columns")

        if not values[0]:
            errors.append("Column 'userId' should not be empty")
        elif values[0] == "NULL":
            errors.append("Column 'userId' should not be 'NULL'")
        elif values[0] in self.seen_user_ids:
            errors.append(f"Duplicate userId found: {values[0]}")
        else:
            self.seen_user_ids.add(values[0])

        if values[1] != "TRUE":
            errors.append("Column 'shouldJoin' should be 'TRUE'")
        
        try:
            join_date = int(values[2])
            is_valid_unix_timestamp, timestamp_message = _is_unix_millisecond_timestamp(join_date)
            if not is_valid_unix_timestamp:
                errors.append(f"Column 'joinDate': {timestamp_message}")
            else:
                is_past, past_message = _is_past_timestamp(join_date)
                if not is_past:
                    errors.append("Column 'joinDate' should be a past UNIX timestamp in milliseconds")
        except ValueError:
            errors.append("Column 'joinDate' should be an integer (UNIX timestamp in milliseconds)")
        
        if values[4] or values[5]:
            errors.append("Columns 'tierEntryAt' and 'tierCalcAt' should be empty")
        
        if values[6] not in ["TRUE", "FALSE"]:
            errors.append("Column 'shouldReward' should be 'TRUE' or 'FALSE'")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, ""