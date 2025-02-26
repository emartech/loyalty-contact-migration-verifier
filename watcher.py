import os
import time
import csv
from src.vouchers.voucher_csv_validator import VoucherValidator
from src.contacts.contacts_csv_validator import ContactsValidator
from src.points.points_csv_validator import PointsValidator
from src.core.logger import Logger

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
        
        # Log error for BOM
        return False, "The file started with a Byte Order Mark (BOM), which is not supported."
    
    return True, ""

def check_user_id(row, user_id_lines, null_user_id_lines, line_number):
    if row['userId'] is None or row['userId'] == "NULL" or row['userId'] == "null":
        # Track NULL userId lines separately
        if 'NULL' not in null_user_id_lines:
            null_user_id_lines['NULL'] = []
        null_user_id_lines['NULL'].append(line_number)
        return False
        
    if row['userId'] in user_id_lines:
        # Add current line to the list of lines with this userId
        user_id_lines[row['userId']].append(line_number)
    else:
        # First time seeing this userId - initialize the list with current line
        user_id_lines[row['userId']] = [line_number]
    return True

def log_user_id_errors(user_id_lines, null_user_id_lines, error_logger, errors):
    # Log NULL userIds
    if 'NULL' in null_user_id_lines:
        for line in null_user_id_lines['NULL']:
            error_message = f"Line {line}: Contact has a NULL or 'NULL' userId"
            errors.append(error_message)
    
    # Log duplicate userIds
    for user_id, lines in user_id_lines.items():
        if len(lines) > 1:
            # This is a duplicate - log all instances
            for line in lines:
                error_message = f"Line {line}: Duplicate userId found: {user_id}"
                errors.append(error_message)

watch_directory = os.path.join(".", "watch_folder")
previous_files = set(os.listdir(watch_directory))

def has_file_stopped_growing(file_path):
    size_before = os.path.getsize(file_path)
    time.sleep(1)
    size_after = os.path.getsize(file_path)
    return size_before == size_after

def write_summary_log(error_log_path, filename, errors):
    """Write a summary of errors to the log file."""
    error_count = len(errors)
    
    if error_count > 100:
        summary = f"The {filename} file contains more than 100 errors:"
    else:
        summary = f"The {filename} file contains {error_count} errors:"
    
    # Write the summary and errors to the log file
    with open(error_log_path, 'w') as log_file:
        log_file.write(summary + "\n\n")
        for error in errors:
            log_file.write(error + "\n")

def classify_csv(file_path):
    # Prepare error log
    error_log_path = os.path.join(watch_directory, "error", os.path.splitext(os.path.basename(file_path))[0] + ".log")
    error_logger = Logger(error_log_path) 
    errors = []
    # Try to decode using utf-8 first
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except UnicodeDecodeError:
        # Log error for UnicodeDecodeError
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            content = file.read()
    error , error_message = _check_for_non_printable_start(file_path)
    if error == False:
        # Log error for non-printable start
        error_logger.log(error_message)
        errors.append(error_message)
        
    # Now, process the cleaned content
    reader = csv.DictReader(content.splitlines())
    headers = reader.fieldnames  # Extract the headers

    contacts_headers = ["userId", "shouldJoin", "joinDate", "tierName", "tierEntryAt", "tierCalcAt", "shouldReward"]
    points_headers = ["userId", "pointsToSpend", "statusPoints", "cashback", "allocatedAt", "expireAt", "setPlanExpiration", "reason", "title", "description"]
    vouchers_headers = ["userId", "externalId", "voucherType", "voucherName", "iconName", "code", "expiration"]

    # Check exact header and create corresponding validator
    if headers == contacts_headers:
        seen_user_ids = set()
        user_id_lines = {}
        null_user_id_lines = {}
        for line_number, row in enumerate(reader, start=2):  # Start at 2 to account for header line
            check_user_id(row, user_id_lines, null_user_id_lines, line_number)
        log_user_id_errors(user_id_lines, null_user_id_lines, error_logger, errors)
        # Create an instance of the validator
        validator = ContactsValidator(file_path, error_log_path, contacts_headers)
    elif headers == points_headers:
        # Create an instance of the validator
        validator = PointsValidator(file_path, error_log_path, points_headers)
    elif headers == vouchers_headers:
        # Create an instance of the validator
        validator = VoucherValidator(file_path, error_log_path, vouchers_headers)
    else:
        # Log error for mismatched headers
        error_message = generate_error_message(os.path.basename(file_path), headers, contacts_headers, points_headers, vouchers_headers)
        error_logger.log(error_message)
        errors.append(error_message)
    
    # Validate the CSV
    if errors:
        write_summary_log(error_log_path, os.path.basename(file_path), errors)
        return False
    return validator.validate()

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
            print("File found validating: " + os.path.basename(full_path))
            is_valid = classify_csv(full_path)
            if is_valid:
                # Move the file to the success folder
                os.rename(full_path, os.path.join(watch_directory, "success", os.path.basename(full_path)))
                print("Validation finished the file " + os.path.basename(full_path) + " is valid")
            else:
                # Move the file to the error folder
                os.rename(full_path, os.path.join(watch_directory, "error", os.path.basename(full_path)))
                print("Validation finished the file " + os.path.basename(full_path) + " has errors")

    previous_files = current_files
    time.sleep(5)  # Check every 5 seconds
