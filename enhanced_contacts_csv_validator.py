
import time

class EnhancedContactsCSVValidator:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.delimiter = ','
        self.expected_columns = ['userId', 'shouldJoin', 'joinDate', 'tierName', 'tierEntryAt', 'tierCalcAt', 'shouldReward']

    def _load_csv(self):
        # Load the CSV file, skipping empty lines
        with open(self.csv_path, 'r') as file:
            content = [line for line in file.readlines() if line.strip()]
        return content

    def validate(self):
        content = self._load_csv()
        header = content[0].strip().split(self.delimiter)

        # Validate column order and presence
        if header != self.expected_columns:
            return False, "Incorrect column order or missing columns"

        # Validate each row
        for row in content[1:]:
            values = row.strip().split(self.delimiter)
            is_valid, error_message = self._validate_row(values)
            if not is_valid:
                return False, f"Incorrect data in row: {row}. {error_message}"

        return True, "CSV is valid"

    def _validate_row(self, values):
        # Validate shouldJoin
        if values[1] != "TRUE":
            return False, "Column 'shouldJoin' should be 'TRUE'"
        
        # Validate joinDate
        try:
            join_date = int(values[2])
            if not self._is_past_timestamp(join_date):
                return False, "Column 'joinDate' should be a past UNIX timestamp in milliseconds"
        except ValueError:
            return False, "Column 'joinDate' should be an integer (UNIX timestamp in milliseconds)"
        
        # Validate tierEntryAt and tierCalcAt
        if values[4] or values[5]:
            return False, "Columns 'tierEntryAt' and 'tierCalcAt' should be empty"
        
        # Validate shouldReward
        if values[6] not in ["TRUE", "FALSE"]:
            return False, "Column 'shouldReward' should be 'TRUE' or 'FALSE'"
        
        return True, ""

    def _is_past_timestamp(self, timestamp_millis):
        # Get current time in milliseconds
        current_time_millis = int(time.time() * 1000)
        return timestamp_millis < current_time_millis
