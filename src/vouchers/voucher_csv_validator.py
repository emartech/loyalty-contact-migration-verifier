import time
import csv

from src.utils.time_utils import _is_past_timestamp, _is_unix_millisecond_timestamp

class VoucherValidator:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.delimiter = ','
        self.expected_columns = ['userId', 'externalId', 'voucherType', 'voucherName', 'iconName', 'code', 'expiration']
        self.default_icon = "basket-colors-1"

    def _load_csv(self):
        with open(self.csv_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file, delimiter=self.delimiter, quotechar='"')
            content = [row for row in reader if any(row)]
            # content = [line for line in file.readlines() if line.strip()]
        return content

    def validate(self):
        content = self._load_csv()
        headers = content[0]
        # headers = content[0].strip().split(self.delimiter)
        if ("userId" not in headers or "externalId" not in headers):
            return False, f"Line 1: Both 'userId' and 'externalId' should be present:\n{content[0]}"
        if set(headers) - {"userId", "externalId"} != set(self.expected_columns) - {"userId", "externalId"}:
            return False, f"Line 1: Incorrect or missing columns. Line content:\n{content[0]}"
        for idx, row in enumerate(content[1:], start=2):  # start=2 because we're skipping the header
            values = row
            # values = row.strip().split(self.delimiter)
            is_valid, error_message = self._validate_row(values)
            if not is_valid:
                return False, f"Error: {error_message}\nRow {idx}:\n{content[0]}\n{row}"
        return True, "CSV is valid"

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