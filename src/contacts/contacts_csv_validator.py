
import time
from src.utils.time_utils import _is_past_timestamp, _is_unix_millisecond_timestamp
from src.core.validator import Validator

class ContactsValidator(Validator):
    contact_columns = ['userId', 'shouldJoin', 'joinDate', 'tierName', 'tierEntryAt', 'tierCalcAt', 'shouldReward']

    def __init__(self, csv_path, log_path, expected_columns=contact_columns):
        super().__init__(csv_path=csv_path, log_path=log_path, expected_columns=expected_columns)

    def _validate_row(self, values):
        errors = []
        if len(values) != len(self.expected_columns):
            error_message = f"Row should have {len(self.expected_columns)} columns"
            errors = errors + [error_message]
            # If there are not enough fields in the row there is no need for further validation
            return False, errors

        if not values[0]:
            error_message = "Column 'userId' should not be empty"
            errors = errors + [error_message]
        # Validate shouldJoin
        if values[1] != "TRUE":
            error_message = "Column 'shouldJoin' should be 'TRUE'"
            errors = errors + [error_message]
        
        # Validate joinDate
        try:
            join_date = int(values[2])
            if not _is_past_timestamp(join_date):
                error_message = "Column 'joinDate' should be a past UNIX timestamp in milliseconds"
                errors = errors + [error_message]
            is_valid_unix_timestampe, message = _is_unix_millisecond_timestamp(join_date)
            if not is_valid_unix_timestampe:
                error_message =  message
                errors = errors + [error_message]
        except ValueError:
            error_message = "Column 'joinDate' should be an integer (UNIX timestamp in milliseconds)"
            errors = errors + [error_message]
        
        # Validate tierEntryAt and tierCalcAt
        if values[4] or values[5]:
            error_message = "Columns 'tierEntryAt' and 'tierCalcAt' should be empty"
            errors = errors + [error_message]
        
        # Validate shouldReward
        if values[6] not in ["TRUE", "FALSE"]:
            error_message = "Column 'shouldReward' should be 'TRUE' or 'FALSE'"
            errors = errors + [error_message]
        
        if len(errors) > 0:
            return False, errors
        
        return True, ""
        