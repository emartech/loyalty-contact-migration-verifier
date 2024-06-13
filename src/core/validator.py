import csv

class Validator:
    def __init__(self, csv_path, expected_columns):
        self.csv_path = csv_path
        self.delimiter = ','
        self.expected_columns = expected_columns

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
            return False, ["Incorrect column order or missing columns"]

        # Validate each row
        errors = []
        for idx, row in enumerate(content[1:], start=2):  # Start from 2 to account for 1-indexed human-readable row numbers
            is_valid, error_message = self._validate_row(row)
            if not is_valid:
                error_message = [f"Error: {error_message} Row {idx}: {row}"]
                errors = errors + error_message
        
        if len(errors) > 0:
            return False, errors
        
        return True, "CSV is valid"

    def _validate_row(self, values: list[str]) -> tuple[bool, str]:
        if len(values) != len(self.expected_columns):
            return False, f"Row should have {len(self.expected_columns)} columns"
        return True, ""
    