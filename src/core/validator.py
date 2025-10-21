import csv
from src.core.logger import Logger

class Validator:
    def __init__(self, csv_path, log_path, expected_columns):
        self.csv_path = csv_path
        self.delimiter = ','
        self.expected_columns = expected_columns
        self.error_logger = Logger(log_path=log_path)

    def _load_csv(self):
        with open(self.csv_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file, delimiter=self.delimiter, quotechar='"') # quotechar is needed to handle quotes in the csv
            content = [row for row in reader if any(row)]
        return content

    def validate(self):
        content = self._load_csv()
        headers = content[0]
        
        # This could be removed as we are checking the header before creating the validator already
        # Validate column order and presence
        if headers != self.expected_columns:
            error_message = "Incorrect column order or missing columns"
            self.error_logger.log(error_message)
            return False

        # Validate each row
        has_errors = False
        for idx, row in enumerate(content[1:], start=2):  # Start from 2 to account for 1-indexed human-readable row numbers
            is_valid, row_errors = self._validate_row(row)
            if not is_valid:
                has_errors = True
                row_error_message = f"Error: {row_errors} Row {idx}: {row}"
                self.error_logger.log(row_error_message)
        
        if has_errors:
            return False
        
        return True

    def _validate_row(self, values: list[str]) -> tuple[bool, str]:
        if len(values) != len(self.expected_columns):
            return False, f"Row should have {len(self.expected_columns)} columns"
        return True, ""
