import time

class PointsCSVValidator:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.delimiter = ','  # Assuming the same delimiter as the previous validator
        self.expected_columns = ["userId", "pointsToSpend", "statusPoints", "cashback", "allocatedAt", "expireAt", "setPlanExpiration", "reason", "title", "description"]

    def _load_csv(self):
        with open(self.csv_path, 'r', encoding='utf-8-sig') as file:  # Handle BOM with encoding
            content = [line for line in file.readlines() if line.strip()]
        return content

    def validate(self):
        content = self._load_csv()
        headers = content[0].strip().split(self.delimiter)
        if headers != self.expected_columns:
            return False, f"Incorrect columns. Expected: {', '.join(self.expected_columns)}. Found: {', '.join(headers)}"
        
        for index, row in enumerate(content[1:], start=2):  # Start from 2 to account for 1-indexed human-readable row numbers
            values = row.strip().split(self.delimiter)
            is_valid, error_message = self._validate_row(values, index, row)
            if not is_valid:
                return False, error_message
                
        return True, "CSV is valid"

    def _validate_row(self, values, row_number, row_content):
        # Validate pointsToSpend
        if not values[1].isdigit():
            return False, f"Error in line {row_number} ({row_content}): pointsToSpend should be a positive integer"

        # Validate statusPoints
        if not values[2].isdigit():
            return False, f"Error in line {row_number} ({row_content}): statusPoints should be a positive integer"

        # Validate cashback
        if values[3]:  # Check if cashback is not empty
            try:
                cashback_value = float(values[3])
                if cashback_value < 0:
                    return False, f"Error in line {row_number} ({row_content}): cashback should be a positive float"
            except ValueError:
                return False, f"Error in line {row_number} ({row_content}): cashback should be a positive float or empty"


        # Validate expireAt and setPlanExpiration
        if values[6].lower() == "true":
            if values[5]:  # If there's a value in expireAt
                return False, f"Error in line {row_number} ({row_content}): If setPlanExpiration is TRUE, expireAt should be empty"
        elif values[6].lower() == "false":
            try:
                expiration = int(values[5])
                if not self._is_future_timestamp(expiration):
                    return False, f"Error in line {row_number} ({row_content}): expireAt should be a future UNIX timestamp in milliseconds when setPlanExpiration is FALSE"
            except ValueError:
                return False, f"Error in line {row_number} ({row_content}): expireAt should be an integer (UNIX timestamp in milliseconds) when setPlanExpiration is FALSE"
        else:
            return False, f"Error in line {row_number} ({row_content}): setPlanExpiration should be either TRUE or FALSE"

        return True, ""

    def _is_future_timestamp(self, timestamp_millis):
        current_time_millis = int(time.time() * 1000)
        return timestamp_millis > current_time_millis