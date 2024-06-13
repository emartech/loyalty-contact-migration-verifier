class Validator:
    def __init__(self, csv_path, expected_columns):
        self.csv_path = csv_path
        self.delimiter = ','
        self.expected_columns = expected_columns

    def _load_csv(self):
        # Load the CSV file, skipping empty lines
        with open(self.csv_path, 'r', encoding='utf-8-sig') as file:
            content = [line for line in file.readlines() if line.strip()]
        return content

    def validate(self):
        content = self._load_csv()
        headers = content[0].strip().split(self.delimiter)
        
        # This could be removed as we are checking the header before creating the validator already
        # Validate column order and presence
        if headers != self.expected_columns:
            return False, ["Incorrect column order or missing columns"]

        # Validate each row
        errors = []
        for idx, row in enumerate(content[1:], start=2):  # Start from 2 to account for 1-indexed human-readable row numbers
            values = row.strip().split(self.delimiter)
            is_valid, error_message = self._validate_row(values)
            if not is_valid:
                error_message = f"Error: {error_message} Row {idx}: {content[0]}{row}"
                errors.append(error_message)
        
        if errors.count() > 0:
            return False, errors
        
        return True, "CSV is valid"

    def _validate_row(self, values: list[str]) -> tuple[bool, str]:
        if len(values) != len(self.expected_columns):
            return False, f"Row should have {len(self.expected_columns)} columns"
        return True, ""
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