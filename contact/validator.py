from enhanced_contacts_csv_validator import EnhancedContactsCSVValidator

# Path to the CSV you want to validate
csv_path = "/Users/i525277/Downloads/OneDrive_1_13-10-2023/L_contacts_HU.csv"

# Create an instance of the validator
validator = EnhancedContactsCSVValidator(csv_path)

# Validate the CSV
is_valid, message = validator.validate()

# Print the results
if is_valid:
    print("The CSV is valid!")
else:
    print(f"Validation failed: {message}")
