import os
import time
import csv
from datetime import datetime
from src.vouchers.voucher_csv_validator import VoucherValidator
from src.contacts.contacts_csv_validator import ContactsValidator
from src.points.points_csv_validator import PointsValidator
from src.core.logger import Logger

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def colored_print(message, color=Colors.RESET):
    """Print message with color"""
    print(f"{color}{message}{Colors.RESET}")

def print_header():
    """Print a welcome header with script information."""
    colored_print("=" * 60, Colors.BOLD + Colors.CYAN)
    colored_print("    LOYALTY CONTACT MIGRATION VALIDATOR", Colors.BOLD + Colors.CYAN)
    colored_print("=" * 60, Colors.BOLD + Colors.CYAN)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def ensure_directories_exist():
    """Ensure the necessary directories exist. If not, create them."""
    directories = [
        os.path.join(".", "watch_folder", "success"),
        os.path.join(".", "watch_folder", "error"),
        os.path.join(".", "watch_folder", "logs")
    ]
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                colored_print(f"❌ Error creating directory {directory}: {e}", Colors.RED)
                raise

print_header()

ensure_directories_exist()

colored_print("📁 Setting up directories...", Colors.BLUE)
print(f"   Watch directory: {os.path.abspath(os.path.join('.', 'watch_folder'))}")
print(f"   Success folder:  {os.path.abspath(os.path.join('.', 'watch_folder', 'success'))}")
print(f"   Error folder:    {os.path.abspath(os.path.join('.', 'watch_folder', 'error'))}")
print(f"   Logs folder:     {os.path.abspath(os.path.join('.', 'watch_folder', 'logs'))}")
print()
colored_print("📋 Supported file types:", Colors.BLUE)
print("   • Contacts CSV (userId, shouldJoin, joinDate, tierName, tierEntryAt, tierCalcAt, shouldReward)")
print("   • Points CSV   (userId, pointsToSpend, statusPoints, cashback, allocatedAt, expireAt, setPlanExpiration, reason, title, description)")
print("   • Vouchers CSV (userId, externalId, voucherType, voucherName, iconName, code, expiration)")
print()
colored_print("📥 To validate files: Drop your CSV files into the watch_folder directory", Colors.GREEN)
print()
colored_print("🔍 Watching for new CSV files... (Press Ctrl+C to stop)", Colors.YELLOW)
colored_print("-" * 60, Colors.CYAN)


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
        print(f"   ⚠️  UTF-8 BOM detected in file")
        # Find a new name for the new file using generate_unique_filename
        new_name = generate_unique_filename(os.path.join(".", "watch_folder"), os.path.basename(file_path))
        # update the file_path with the new_name
        file_path_edited = os.path.join(".", "watch_folder", new_name)
        # Save the modified content without BOM to the watch_folder
        with open(file_path_edited, 'wb') as file:
            file.write(content[3:])
        
        colored_print(f"   🔧 Created cleaned version: {new_name}", Colors.YELLOW)
        colored_print(f"   📝 BOM removed from file header", Colors.YELLOW)
        
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

processed_files = {'success': 0, 'error': 0}
files_processed = False

def has_file_stopped_growing(file_path):
    try:
        size_before = os.path.getsize(file_path)
        time.sleep(2)  # Increased wait time for better reliability
        size_after = os.path.getsize(file_path)
        return size_before == size_after
    except OSError:
        # File might have been moved or deleted during check
        return True

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
    print("   🔍 Analyzing file encoding...")
    # Prepare error log
    error_log_path = os.path.join(watch_directory, "logs", os.path.splitext(os.path.basename(file_path))[0] + ".log")
    error_logger = Logger(error_log_path) 
    errors = []
    # Try to decode using utf-8 first
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        print("   ✅ File encoding: UTF-8")
    except UnicodeDecodeError:
        print("   ⚠️  UTF-8 failed, trying ISO-8859-1 encoding...")
        # Log error for UnicodeDecodeError
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            content = file.read()
        print("   ✅ File encoding: ISO-8859-1")
    
    print("   🔍 Checking for file format issues...")
    is_valid, error_message = _check_for_non_printable_start(file_path)
    if is_valid == False:
        # Log error for non-printable start
        error_logger.log(error_message)
        errors.append(error_message)
        
    print("   🏗️  Parsing CSV structure...")
    
    contacts_headers = ["userId", "shouldJoin", "joinDate", "tierName", "tierEntryAt", "tierCalcAt", "shouldReward"]
    points_headers = ["userId", "pointsToSpend", "statusPoints", "cashback", "allocatedAt", "expireAt", "setPlanExpiration", "reason", "title", "description"]
    vouchers_headers = ["userId", "externalId", "voucherType", "voucherName", "iconName", "code", "expiration"]
    
    # Try to parse as regular comma-separated CSV first
    content_lines = content.splitlines()
    reader = csv.DictReader(content_lines)
    headers = reader.fieldnames  # Extract the headers
    
    # If headers don't match, log error and skip separator fixing (function not defined)
    if headers not in [contacts_headers, points_headers, vouchers_headers]:
        print(f"   📋 Headers found: {len(headers) if headers else 0} columns")
        print("   🔍 Header format doesn't match expected. Skipping separator fix (function not defined)...")
    
    print(f"   📋 Final headers: {len(headers) if headers else 0} columns")
    print("   🔍 Identifying CSV type...")
    # Check exact header and create corresponding validator
    if headers == contacts_headers:
        print("   ✅ Detected: CONTACTS CSV")
        print("   🔍 Checking for duplicate/null user IDs...")
        seen_user_ids = set()
        user_id_lines = {}
        null_user_id_lines = {}
        for line_number, row in enumerate(reader, start=2):  # Start at 2 to account for header line
            check_user_id(row, user_id_lines, null_user_id_lines, line_number)
        log_user_id_errors(user_id_lines, null_user_id_lines, error_logger, errors)
        print("   🏗️  Creating contacts validator...")
        # Create an instance of the validator
        validator = ContactsValidator(file_path, error_log_path, contacts_headers)
    elif headers == points_headers:
        print("   ✅ Detected: POINTS CSV")
        print("   🏗️  Creating points validator...")
        # Create an instance of the validator
        validator = PointsValidator(file_path, error_log_path, points_headers)
    elif headers == vouchers_headers:
        print("   ✅ Detected: VOUCHERS CSV")
        print("   🏗️  Creating vouchers validator...")
        # Create an instance of the validator
        validator = VoucherValidator(file_path, error_log_path, vouchers_headers)
    else:
        print("   ❌ Unknown CSV type - headers don't match expected format")
        # Log error for mismatched headers
        error_message = generate_error_message(os.path.basename(file_path), headers, contacts_headers, points_headers, vouchers_headers)
        error_logger.log(error_message)
        errors.append(error_message)
        validator = None
    
    # Validate the CSV
    if errors or validator is None:
        print("   ❌ Pre-validation errors found")
        write_summary_log(error_log_path, os.path.basename(file_path), errors)
        if '_temp_corrected.csv' in file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"   ⚠️  Warning: Could not remove temporary file: {e}")
        return False
    
    print("   🔄 Running detailed validation...")
    result = validator.validate()
    
    # Clean up temporary file if it exists
    if '_temp_corrected.csv' in file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"   ⚠️  Warning: Could not remove temporary file: {e}")
        
    return result

def generate_error_message(filename, headers_found, contacts_headers, points_headers, vouchers_headers):
    error_msg = f"The header in file {filename} does not match any of the expected headers:\n"
    headers_str = ', '.join(headers_found) if headers_found else "No headers found or file is empty"
    error_msg += f"\nFailed:      {headers_str}"
    error_msg += f"\nContacts:    {', '.join(contacts_headers)}"
    error_msg += f"\nPoints:      {', '.join(points_headers)}"
    error_msg += f"\nVouchers:    {', '.join(vouchers_headers)}"
    return error_msg

try:
    timeout_start_time = None
    
    while True:
        current_files = set(os.listdir(watch_directory))
        new_files = current_files - previous_files

        for file in new_files:
            if file.endswith(".csv"):
                # Skip auto-generated corrected files to avoid reprocessing
                if '_comma_fixed' in file:
                    colored_print(f"   ⏭️  Skipping auto-generated comma-fixed file: {file}", Colors.CYAN)
                    continue
                    
                full_path = os.path.join(watch_directory, file)
                file_size = os.path.getsize(full_path)
                colored_print(f"\n📄 New file detected: {file}", Colors.BOLD + Colors.BLUE)
                print(f"   Size: {file_size:,} bytes")
                colored_print("   Waiting for file transfer to complete...", Colors.YELLOW)
                
                while not has_file_stopped_growing(full_path):
                    colored_print("   ⏳ File still growing, waiting...", Colors.YELLOW)
                    
                colored_print(f"   ✅ File transfer complete, starting validation...", Colors.GREEN)
                
                start_time = time.time()
                is_valid = classify_csv(full_path)
                processing_time = time.time() - start_time
                
                colored_print(f"\n📊 PROCESSING COMPLETE", Colors.BOLD + Colors.PURPLE)
                print(f"   Original file: {file}")
                print(f"   Processing time: {processing_time:.2f} seconds")
                
                if is_valid:
                    # Move the file to the success folder
                    destination = os.path.join(watch_directory, "success", os.path.basename(full_path))
                    try:
                        os.rename(full_path, destination)
                        colored_print(f"   ✅ Status: VALID", Colors.BOLD + Colors.GREEN)
                        print(f"   📁 Moved to: success/{os.path.basename(full_path)}")
                        processed_files['success'] += 1
                    except OSError as e:
                        colored_print(f"   ⚠️  Error moving file to success folder: {e}", Colors.RED)
                        processed_files['error'] += 1
                else:
                    # Move the file to the error folder
                    destination = os.path.join(watch_directory, "error", os.path.basename(full_path))
                    try:
                        os.rename(full_path, destination)
                        error_log = os.path.join(watch_directory, "logs", os.path.splitext(os.path.basename(full_path))[0] + ".log")
                        colored_print(f"   ❌ Status: ERRORS FOUND", Colors.BOLD + Colors.RED)
                        print(f"   📁 Moved to: error/{os.path.basename(full_path)}")
                        print(f"   📋 Error log: logs/{os.path.splitext(os.path.basename(full_path))[0]}.log")
                        processed_files['error'] += 1
                    except OSError as e:
                        colored_print(f"   ⚠️  Error moving file to error folder: {e}", Colors.RED)
                        processed_files['error'] += 1
                
                files_processed = True
                
                # Start timeout countdown after processing first file
                if timeout_start_time is None:
                    timeout_start_time = time.time()
                    print()
                    colored_print(f"⏰ Auto-completion timer started (10 seconds)", Colors.YELLOW)
                
                colored_print("-" * 60, Colors.CYAN)

        previous_files = current_files
        
        # Check for timeout if at least one file has been processed
        if files_processed and timeout_start_time is not None:
            elapsed_time = time.time() - timeout_start_time
            remaining_time = 10 - elapsed_time
            
            if elapsed_time >= 10:
                print()  # Clear the countdown line
                colored_print(f"⏰ Auto-completion timeout reached", Colors.YELLOW)
                print()
                colored_print(f"📊 Final Statistics:", Colors.BOLD + Colors.CYAN)
                print(f"   ✅ Successfully processed: {processed_files['success']} files")
                print(f"   ❌ Files with errors: {processed_files['error']} files")
                print(f"   📁 Total processed: {processed_files['success'] + processed_files['error']} files")
                print()
                colored_print(f"👋 Auto-completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.BOLD + Colors.GREEN)
                break
            elif remaining_time > 0:
                # Clear the line and rewrite with proper spacing
                print(f"\r⏳ Auto-completion in {remaining_time:.1f}s (Ctrl+C to stop early)" + " " * 20, end='\r')
        
        time.sleep(1)  # Check every 1 second for better timeout precision

except KeyboardInterrupt:
    print()  # Clear any countdown line
    print()
    colored_print("🛑 Shutdown requested by user", Colors.YELLOW)
    print()
    colored_print("📊 Final Statistics:", Colors.BOLD + Colors.CYAN)
    
    print(f"   ✅ Successfully processed: {processed_files['success']} files")
    print(f"   ❌ Files with errors: {processed_files['error']} files")
    print(f"   📁 Total processed: {processed_files['success'] + processed_files['error']} files")
    print()
    colored_print(f"👋 Goodbye! Watcher stopped at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.BOLD + Colors.GREEN)
    
except Exception as e:
    print()  # Clear any countdown line
    print()
    colored_print(f"💥 Unexpected error occurred: {str(e)}", Colors.BOLD + Colors.RED)
    colored_print("🔄 Please restart the watcher", Colors.YELLOW)
