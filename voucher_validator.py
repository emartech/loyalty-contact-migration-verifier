from voucher_csv_validator_content import VoucherCSVValidatorBOM

# Path to the CSV you want to validate
csv_path = "/Users/i525277/Downloads/L_voucher_ATDE_claimed_v4.csv"

# Create an instance of the validator
validator = VoucherCSVValidatorBOM(csv_path)

# Validate the CSV
is_valid, message = validator.validate()

# Print the results
if is_valid:
    print("The CSV is valid!")
else:
    print(f"Validation failed: {message}")
