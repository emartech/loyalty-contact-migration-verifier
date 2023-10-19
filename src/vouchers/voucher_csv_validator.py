import time
from src.utils.time_utils import _is_past_timestamp, _is_unix_millisecond_timestamp

class VoucherValidator:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.delimiter = ','
        self.expected_columns = ['userId', 'externalId', 'voucherType', 'voucherName', 'iconName', 'code', 'expiration']
        self.default_icon = "basket-colors-1"

    def _load_csv(self):
        with open(self.csv_path, 'r', encoding='utf-8-sig') as file:
            content = [line for line in file.readlines() if line.strip()]
        return content

    def validate(self):
        content = self._load_csv()
        headers = content[0].strip().split(self.delimiter)
        if ("userId" not in headers or "externalId" not in headers):
            return False, f"Line 1: Both 'userId' and 'externalId' should be present:\n{content[0]}"
        if set(headers) - {"userId", "externalId"} != set(self.expected_columns) - {"userId", "externalId"}:
            return False, f"Line 1: Incorrect or missing columns. Line content:\n{content[0]}"
        for index, row in enumerate(content[1:], start=2):  # start=2 because we're skipping the header
            values = row.strip().split(self.delimiter)
            is_valid, error_message = self._validate_row(values)
            if not is_valid:
                return False, f"Line {index}: {error_message}. Line content:\n{row}"
        return True, "CSV is valid"

    def _validate_row(self, values):
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
            if not _is_unix_millisecond_timestamp(expiration):
                return False, "Column 'expiration' should be a valid UNIX timestamp in milliseconds"
            if _is_past_timestamp(expiration):
                return False, "Column 'expiration' should be a future UNIX timestamp in milliseconds"
        except ValueError:
            return False, "Column 'expiration' should be an integer (UNIX timestamp in milliseconds)"
        return True, ""