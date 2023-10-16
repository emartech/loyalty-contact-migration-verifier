import os
import time
import csv
from src.vouchers.voucher_csv_validator_content import VoucherCSVValidatorBOM
from src.contact.enhanced_contacts_csv_validator import EnhancedContactsCSVValidator
from src.points.points_csv_validator import PointsCSVValidator


def ensure_directories_exist():
    """Ensure the necessary directories exist. If not, create them."""
    directories = [os.path.join(".", "watch_folder", "success"), os.path.join(".", "watch_folder", "error")]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

ensure_directories_exist()

watch_directory = os.path.join(".", "watch_folder")
previous_files = set(os.listdir(watch_directory))

def has_file_stopped_growing(file_path):
    size_before = os.path.getsize(file_path)
    time.sleep(1)
    size_after = os.path.getsize(file_path)
    return size_before == size_after

def classify_csv(file_path):
    # Try to decode using utf-8 first
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        # If utf-8 fails, try ISO-8859-1
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            content = file.read()

    # Clean the content by removing non-printable characters
    content = ''.join(ch for ch in content if ch.isprintable() or ch.isspace())
    
    # Now, process the cleaned content
    reader = csv.reader(content.splitlines())
    headers = next(reader)  # Extract the first line, which is the header

    contacts_headers = ["userId", "shouldJoin", "joinDate", "tierName", "tierEntryAt", "tierCalcAt", "shouldReward"]
    points_headers = ["userId", "pointsToSpend", "statusPoints", "cashback", "allocatedAt", "expireAt", "setPlanExpiration", "reason", "title", "description"]
    vouchers_headers = ["userId", "externalId", "voucherType", "voucherName", "iconName", "code", "expiration"]

    # Check exact match
    if headers == contacts_headers:
        # Create an instance of the validator
        validator = EnhancedContactsCSVValidator(file_path)

        # Validate the CSV
        is_valid, message = validator.validate()

        if is_valid:
            message = "contacts", "The CSV is valid!"
        else:
            message = "error", f"Validation failed: {message}"
        return message
    elif headers == points_headers:
        # Create an instance of the validator
        validator = PointsCSVValidator(file_path)

        # Validate the CSV
        is_valid, message = validator.validate()

        if is_valid:
            message = "points", "The CSV is valid!"
        else:
            message = "error", f"Validation failed: {message}"
        return message
    elif headers == vouchers_headers:
        # Create an instance of the validator
        validator = VoucherCSVValidatorBOM(file_path)

        # Validate the CSV
        is_valid, message = validator.validate()

        if is_valid:
            message = "vouchers", "The CSV is valid!"
        else:
            message = "error", f"Validation failed: {message}"
        return message
    else:
        return "error", generate_error_message(os.path.basename(file_path), headers, contacts_headers, points_headers, vouchers_headers)

def generate_error_message(filename, headers_found, contacts_headers, points_headers, vouchers_headers):
    error_msg = f"We checked whether the file {filename} in the watch_folder contains the expected columns for the following categories:\n"
    error_msg += f"\nContacts:\n{', '.join(contacts_headers)}"
    error_msg += f"\nPoints:\n{', '.join(points_headers)}"
    error_msg += f"\nVouchers:\n{', '.join(vouchers_headers)}"
    error_msg += f"\nHowever, we detected these columns instead:\n{', '.join(headers_found)}"
    return error_msg

while True:
    current_files = set(os.listdir(watch_directory))
    new_files = current_files - previous_files

    for file in new_files:
        if file.endswith(".csv"):   
            full_path = os.path.join(watch_directory, file)
            while not has_file_stopped_growing(full_path):
                pass
            if classify_csv(full_path)[0] == "error":
                # the second argument is the error message. Save that to a .log file with the same name as the csv
                error_log_path = os.path.join(watch_directory, "error", os.path.splitext(os.path.basename(full_path))[0] + ".log")
                with open(error_log_path, "w") as f:
                    f.write(classify_csv(full_path)[1])
                # Move the file to the error folder
                os.rename(full_path, os.path.join(watch_directory, "error", os.path.basename(full_path)))
            else:
                # Move the file to the success folder
                os.rename(full_path, os.path.join(watch_directory, "success", os.path.basename(full_path)))

    previous_files = current_files
    time.sleep(5)  # Check every 5 seconds



