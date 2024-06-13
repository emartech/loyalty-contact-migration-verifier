
import time
from src.utils.time_utils import _is_past_timestamp, _is_unix_millisecond_timestamp
from src.core.validator import Validator

class ContactsValidator(Validator):
    contact_columns = ['userId', 'shouldJoin', 'joinDate', 'tierName', 'tierEntryAt', 'tierCalcAt', 'shouldReward']

    def __init__(self, csv_path, expected_columns=contact_columns):
        super().__init__(csv_path=csv_path, expected_columns=expected_columns)

    def _validate_row(self, values):
        if len(values) != len(self.expected_columns):
            return False, f"Row should have {len(self.expected_columns)} columns"
        if not values[0]:
            return False, "Column 'userId' should not be empty"
        # Validate shouldJoin
        if values[1] != "TRUE":
            return False, "Column 'shouldJoin' should be 'TRUE'"
        
        # Validate joinDate
        try:
            join_date = int(values[2])
            if not _is_past_timestamp(join_date):
                return False, "Column 'joinDate' should be a past UNIX timestamp in milliseconds"
            is_valid_unix_timestampe, message = _is_unix_millisecond_timestamp(join_date)
            if not is_valid_unix_timestampe:
                return False, message
        except ValueError:
            return False, "Column 'joinDate' should be an integer (UNIX timestamp in milliseconds)"
        
        # Validate tierEntryAt and tierCalcAt
        if values[4] or values[5]:
            return False, "Columns 'tierEntryAt' and 'tierCalcAt' should be empty"
        
        # Validate shouldReward
        if values[6] not in ["TRUE", "FALSE"]:
            return False, "Column 'shouldReward' should be 'TRUE' or 'FALSE'"
        
        return True, ""
        