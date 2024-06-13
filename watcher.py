import os
import time
import csv
from src.vouchers.voucher_csv_validator import VoucherValidator
from src.contacts.contacts_csv_validator import ContactsValidator
from src.points.points_csv_validator import PointsValidator

def ensure_directories_exist():
    """Ensure the necessary directories exist. If not, create them."""
    directories = [
        os.path.join(".", "watch_folder", "success"),
        os.path.join(".", "watch_folder", "error")
    ]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

ensure_directories_exist()


def generate_unique_filename(directory, original_name):
    base, ext = os.path.splitext(original_name)
    counter = 1
    new_name = f"{base}_edited{ext}"
    while os.path.exists(os.path.join(directory, new_name)):
        new_name = f"{base}_edited_{counter}{ext}"
        counter += 1
    return new_name

def _check_for_non_printable_start(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
        
    # Check for UTF-8 BOM
    if content.startswith(b'\xef\xbb\xbf'):
        # Find a new name for the new file using generate_unique_filename
        new_name = generate_unique_filename(os.path.join(".", "watch_folder"), os.path.basename(file_path))
        # update the file_path with the new_name
        file_path_edited = os.path.join(".", "watch_folder", new_name)
        # Save the modified content without BOM to the watch_folder
        with open(file_path_edited, 'wb') as file:
            file.write(content[3:])
        
        return False, "The file started with a Byte Order Mark (BOM), which is not supported."
    
    return True, ""

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
        with open(file_path, 'r') as file:
            content = file.read()
    except UnicodeDecodeError:
        # If utf-8 fails, try ISO-8859-1
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            content = file.read()
    error , error_message = _check_for_non_printable_start(file_path)
    if error == False:
        return "error", error_message
        
    # Now, process the cleaned content
    reader = csv.reader(content.splitlines())
    headers = next(reader)  # Extract the first line, which is the header

    contacts_headers = ["userId", "shouldJoin", "joinDate", "tierName", "tierEntryAt", "tierCalcAt", "shouldReward"]
    points_headers = ["userId", "pointsToSpend", "statusPoints", "cashback", "allocatedAt", "expireAt", "setPlanExpiration", "reason", "title", "description"]
    vouchers_headers = ["userId", "externalId", "voucherType", "voucherName", "iconName", "code", "expiration"]

    # Check exact header and create corresponding validator
    if headers == contacts_headers:
        # Create an instance of the validator
        validator = ContactsValidator(file_path, contacts_headers)
    elif headers == points_headers:
        # Create an instance of the validator
        validator = PointsValidator(file_path, points_headers)
    elif headers == vouchers_headers:
        # Create an instance of the validator
        validator = VoucherValidator(file_path, vouchers_headers)
    else:
        return "error", generate_error_message(os.path.basename(file_path), headers, contacts_headers, points_headers, vouchers_headers)
    # Validate the CSV
    is_valid, message = validator.validate()

    if is_valid:
        message = "contacts", "The CSV is valid!"
    else:
        message = "error", f"Validation failed: {message}"
    return message

def generate_error_message(filename, headers_found, contacts_headers, points_headers, vouchers_headers):
    error_msg = f"The header in file {filename} does not match any of the expected headers:\n"
    error_msg += f"\nFailed:      {', '.join(headers_found)}"
    error_msg += f"\nContacts:    {', '.join(contacts_headers)}"
    error_msg += f"\nPoints:      {', '.join(points_headers)}"
    error_msg += f"\nVouchers:    {', '.join(vouchers_headers)}"
    return error_msg

while True:
    current_files = set(os.listdir(watch_directory))
    new_files = current_files - previous_files

    for file in new_files:
        if file.endswith(".csv"):   
            full_path = os.path.join(watch_directory, file)
            while not has_file_stopped_growing(full_path):
                pass
            error, error_message = classify_csv(full_path)
            if error == "error":
                # the second argument is the error message. Save that to a .log file with the same name as the csv
                error_log_path = os.path.join(watch_directory, "error", os.path.splitext(os.path.basename(full_path))[0] + ".log")
                with open(error_log_path, "w") as f:
                    f.write(error_message)
                # Move the file to the error folder
                os.rename(full_path, os.path.join(watch_directory, "error", os.path.basename(full_path)))
            else:
                # Move the file to the success folder
                os.rename(full_path, os.path.join(watch_directory, "success", os.path.basename(full_path)))

    previous_files = current_files
    time.sleep(5)  # Check every 5 seconds



