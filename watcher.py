# SPDX-FileCopyrightText: 2024 SAP Emarsys
# SPDX-License-Identifier: GPL-3.0-only

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
colored_print("🔍 Checking for existing CSV files in watch folder...", Colors.YELLOW)


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
        
    if content.startswith(b'\xef\xbb\xbf'):
        print(f"   ⚠️  UTF-8 BOM detected in file")
        colored_print(f"   📝 BOM will be handled internally for validation", Colors.YELLOW)
        
        cleaned_content = content[3:].decode('utf-8')
        return False, "The file started with a Byte Order Mark (BOM), which is not supported.", cleaned_content
    
    return True, "", None

def check_user_id(row, user_id_lines, null_user_id_lines, line_number):
    if row['userId'] is None or row['userId'] == "NULL" or row['userId'] == "null":
        if 'NULL' not in null_user_id_lines:
            null_user_id_lines['NULL'] = []
        null_user_id_lines['NULL'].append(line_number)
        return False
        
    if row['userId'] in user_id_lines:
        user_id_lines[row['userId']].append(line_number)
    else:
        user_id_lines[row['userId']] = [line_number]
    return True

def log_user_id_errors(user_id_lines, null_user_id_lines, error_logger, errors):
    if 'NULL' in null_user_id_lines:
        for line in null_user_id_lines['NULL']:
            error_message = f"Line {line}: Contact has a NULL or 'NULL' userId"
            errors.append(error_message)
    
    for user_id, lines in user_id_lines.items():
        if len(lines) > 1:
            for line in lines:
                error_message = f"Line {line}: Duplicate userId found: {user_id}"
                errors.append(error_message)

watch_directory = os.path.join(".", "watch_folder")

processed_files = {'success': 0, 'error': 0}
files_processed = False

def process_existing_files():
    """Process any CSV files that already exist in the watch folder on startup."""
    global files_processed
    existing_csv_files = [f for f in os.listdir(watch_directory) 
                         if f.endswith('.csv') and not '_comma_fixed' in f]
    
    if existing_csv_files:
        colored_print(f"📋 Found {len(existing_csv_files)} existing CSV file(s) to process", Colors.CYAN)
        
        for file in existing_csv_files:
            full_path = os.path.join(watch_directory, file)
            file_size = os.path.getsize(full_path)
            colored_print(f"\n📄 Processing existing file: {file}", Colors.BOLD + Colors.BLUE)
            file_size_mb = file_size / (1024 * 1024)
            if file_size_mb >= 1:
                print(f"   Size: {file_size_mb:.1f} MB ({file_size:,} bytes)")
            else:
                print(f"   Size: {file_size:,} bytes")
            
            start_time = time.time()
            is_valid = classify_csv(full_path)
            processing_time = time.time() - start_time
            
            colored_print(f"\n📊 PROCESSING COMPLETE", Colors.BOLD + Colors.PURPLE)
            print(f"   Original file: {file}")
            print(f"   Processing time: {processing_time:.2f} seconds")
            
            if is_valid:
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
                destination = os.path.join(watch_directory, "error", os.path.basename(full_path))
                try:
                    os.rename(full_path, destination)
                    colored_print(f"   ❌ Status: ERRORS FOUND", Colors.BOLD + Colors.RED)
                    print(f"   📁 Moved to: error/{os.path.basename(full_path)}")
                    print(f"   📋 Error log: logs/{os.path.splitext(os.path.basename(full_path))[0]}.txt")
                    processed_files['error'] += 1
                except OSError as e:
                    colored_print(f"   ⚠️  Error moving file to error folder: {e}", Colors.RED)
                    processed_files['error'] += 1
            
            colored_print("-" * 60, Colors.CYAN)
        
        files_processed = True
        
        return set(os.listdir(watch_directory))
    else:
        colored_print("   ✅ No existing CSV files found", Colors.GREEN)
        return set(os.listdir(watch_directory))

def has_file_stopped_growing(file_path):
    try:
        size_before = os.path.getsize(file_path)
        time.sleep(2)
        size_after = os.path.getsize(file_path)
        return size_before == size_after
    except OSError:
        return True

def write_summary_log(error_log_path, filename, errors, timestamp_error_count=0, validator_error_count=0, validation_error_details=[]):
    """Write a structured summary of errors to the log file."""
    details_filename = None
    if validation_error_details:
        log_dir = os.path.dirname(error_log_path)
        base_name = os.path.splitext(os.path.basename(error_log_path))[0]
        details_filename = f"{base_name}_details.txt"
        counter = 1
        while os.path.exists(os.path.join(log_dir, details_filename)):
            details_filename = f"{base_name}_details_{counter}.txt"
            counter += 1
        details_log_path = os.path.join(log_dir, details_filename)
        
        with open(details_log_path, 'w') as details_file:
            details_file.write("="*80 + "\n")
            details_file.write(f"DETAILED VALIDATION ERRORS FOR: {filename}\n")
            details_file.write("="*80 + "\n\n")
            
            for i, error in enumerate(validation_error_details, 1):
                if " -> Row " in error:
                    error_part, row_part = error.split(" -> Row ", 1)
                    row_num = row_part.split(": ", 1)[0]
                    row_data = row_part.split(": ", 1)[1] if ": " in row_part else ""
                    
                    error_message = error_part.replace("Error: ", "")
                    
                    individual_errors = error_message.split("; ")
                    
                    details_file.write(f"#{i}. ROW {row_num} VALIDATION ERRORS\n")
                    details_file.write("-" * 50 + "\n")
                    
                    for j, individual_error in enumerate(individual_errors, 1):
                        details_file.write(f"   {j}. {individual_error}\n")
                    
                    details_file.write(f"\n   📋 Row Data: {row_data}\n")
                    details_file.write("\n" + "="*80 + "\n\n")
                else:
                    details_file.write(f"#{i}. {error}\n")
                    details_file.write("-" * 50 + "\n\n")
    
    total_errors = len(errors) + timestamp_error_count + validator_error_count
    
    with open(error_log_path, 'w') as log_file:
        log_file.write("="*60 + "\n")
        log_file.write(f"VALIDATION REPORT FOR: {filename}\n")
        log_file.write("="*60 + "\n\n")
        log_file.write(f"❌ TOTAL ERRORS FOUND: {total_errors}\n\n")
        
        error_count = 1
        has_bom_error = any("Byte Order Mark (BOM)" in error for error in errors)
        has_separator_error = any("semicolon" in error and "separators" in error for error in errors)
        has_header_error = any("does not match" in error and "header" in error.lower() for error in errors)
        
        if has_bom_error:
            log_file.write(f"{error_count}. BYTE ORDER MARK (BOM) ERROR\n")
            log_file.write("-" * 40 + "\n")
            log_file.write("❌ Issue: The file started with a Byte Order Mark (BOM)\n")
            log_file.write("💡 Solution: Remove the BOM from the file and save as UTF-8 without BOM\n\n\n")
            error_count += 1
        
        if has_separator_error:
            log_file.write(f"{error_count}. SEPARATOR FORMAT ERROR\n")
            log_file.write("-" * 40 + "\n")
            for error in errors:
                if "semicolon" in error and "separators" in error:
                    log_file.write("❌ Issue: File uses incorrect separator\n")
                    log_file.write(f"{error}\n")
                    log_file.write("💡 Solution: Replace all semicolons (;) with commas (,) in the file\n\n\n")
                    break
            error_count += 1
        
        if timestamp_error_count > 0:
            log_file.write(f"{error_count}. TIMESTAMP FORMAT ERRORS\n")
            log_file.write("-" * 40 + "\n")
            log_file.write(f"❌ Issue: Found {timestamp_error_count} timestamp errors\n")
            log_file.write("💡 Common issues: UNIX timestamp is in seconds instead of milliseconds\n\n\n")
            error_count += 1
            error_count += 1
        
        if validator_error_count > 0:
            log_file.write(f"{error_count}. DATA VALIDATION ERRORS\n")
            log_file.write("-" * 40 + "\n")
            log_file.write(f"❌ Issue: Found {validator_error_count} data validation errors\n")
            log_file.write("💡 Common issues: Invalid field values, empty required fields, incorrect format\n\n\n")
            error_count += 1
        
        if has_header_error:
            log_file.write(f"{error_count}. HEADER FORMAT ERROR\n")
            log_file.write("-" * 40 + "\n")
            for error in errors:
                if "does not match" in error and "header" in error.lower():
                    log_file.write(f"❌ Issue: Headers don't match expected format\n")
                    log_file.write(f"{error}\n")
                    log_file.write("💡 Solution: Update headers to match one of the expected formats above\n\n")
                    break
        
        log_file.write("="*60 + "\n")
        
        if (timestamp_error_count > 0 or validator_error_count > 0) and validation_error_details and details_filename:
            log_file.write(f"📋 Details: See {details_filename} for specific rows and error details\n")
            log_file.write("="*60 + "\n")

def format_file_size(size_bytes):
    """Format file size with appropriate units."""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f}MB"

def check_file_size_and_get_mode(file_path):
    """Check file size and determine processing mode with user warnings."""
    file_size = os.path.getsize(file_path)
    file_size_mb = file_size / (1024 * 1024)
    size_display = format_file_size(file_size)
    
    if file_size_mb > 500:
        colored_print(f"   ❌ File too large: {size_display} (Maximum: 500MB)", Colors.RED)
        colored_print(f"   💡 Please split the file into smaller chunks for processing", Colors.YELLOW)
        return False, "oversized", file_size_mb
    
    elif file_size_mb > 100:
        colored_print(f"   ⚠️  Large file detected: {size_display}", Colors.YELLOW)
        colored_print(f"   📊 This may take several minutes and use significant memory", Colors.YELLOW)
        colored_print(f"   🔄 Processing will use optimized streaming mode", Colors.CYAN)
        return True, "large_file", file_size_mb
    
    elif file_size_mb > 10:
        colored_print(f"   📊 Medium file: {size_display} - using optimized processing", Colors.BLUE)
        return True, "medium_file", file_size_mb
    
    else:
        colored_print(f"   📊 File size: {size_display}", Colors.GREEN)
        return True, "normal", file_size_mb

def count_file_rows(file_path, encoding='utf-8'):
    """Quickly count rows in file for progress tracking."""
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            return sum(1 for line in file) - 1
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            return sum(1 for line in file) - 1

def generate_unique_log_filename(logs_directory, original_name):
    base_name = os.path.splitext(original_name)[0]
    extension = ".txt"
    log_filename = f"{base_name}{extension}"
    counter = 1
    
    while os.path.exists(os.path.join(logs_directory, log_filename)):
        log_filename = f"{base_name}_{counter}{extension}"
        counter += 1
    
    return log_filename

def classify_csv(file_path):
    print("   🔍 Checking file size and requirements...")
    
    size_ok, processing_mode, file_size_mb = check_file_size_and_get_mode(file_path)
    if not size_ok:
        return False
    
    print("   🔍 Analyzing file encoding...")
    logs_directory = os.path.join(watch_directory, "logs")
    original_filename = os.path.basename(file_path)
    unique_log_filename = generate_unique_log_filename(logs_directory, original_filename)
    error_log_path = os.path.join(logs_directory, unique_log_filename)
    error_logger = Logger(error_log_path) 
    errors = []
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        print("   ✅ File encoding: UTF-8")
    except UnicodeDecodeError:
        print("   ⚠️  UTF-8 failed, trying ISO-8859-1 encoding...")
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            content = file.read()
        print("   ✅ File encoding: ISO-8859-1")
    
    print("   🔍 Checking for file format issues...")
    bom_result = _check_for_non_printable_start(file_path)
    has_bom = False
    
    if len(bom_result) == 3:
        is_valid, error_message, cleaned_content = bom_result
        has_bom = not is_valid
        if has_bom:
            errors.append(error_message)
            content = cleaned_content
    else:
        is_valid, error_message = bom_result
        has_bom = False
        if not is_valid:
            errors.append(error_message)
        
    print("   🏗️  Parsing CSV structure...")
    
    contacts_headers = ["userId", "shouldJoin", "joinDate", "tierName", "tierEntryAt", "tierCalcAt", "shouldReward"]
    points_headers = ["userId", "pointsToSpend", "statusPoints", "cashback", "allocatedAt", "expireAt", "setPlanExpiration", "reason", "title", "description"]
    vouchers_headers = ["userId", "externalId", "voucherType", "voucherName", "iconName", "code", "expiration"]
    
    content_lines = content.splitlines()
    reader = csv.DictReader(content_lines)
    headers = reader.fieldnames
    
    delimiter = ','
    if headers not in [contacts_headers, points_headers, vouchers_headers]:
        print(f"   📋 Headers found: {len(headers) if headers else 0} columns")
        print("   🔍 Checking if file uses semicolon separator (unsupported)...")
        try:
            reader = csv.DictReader(content_lines, delimiter=';')
            semicolon_headers = reader.fieldnames
            if semicolon_headers in [contacts_headers, points_headers, vouchers_headers]:
                print("   ⚠️  File uses semicolon separators, but comma is the accepted format")
                separator_error = f"The file uses semicolon (;) separators, but comma (,) is the accepted format.\n\nFound: {'; '.join(semicolon_headers)}\nExpected: {', '.join(semicolon_headers)}"
                errors.append(separator_error)
                headers = semicolon_headers
                delimiter = ';'
            else:
                print("   ❌ Semicolon separator also doesn't match expected format")
        except Exception as e:
            print(f"   ❌ Error trying semicolon separator: {e}")
    
    print(f"   📋 Final headers: {len(headers) if headers else 0} columns")
    print("   🔍 Identifying CSV type...")
    if headers == contacts_headers:
        print("   ✅ Detected: CONTACTS CSV")
        print("   🔍 Checking for duplicate/null user IDs...")
        seen_user_ids = set()
        user_id_lines = {}
        null_user_id_lines = {}
        for line_number, row in enumerate(reader, start=2):
            check_user_id(row, user_id_lines, null_user_id_lines, line_number)
        log_user_id_errors(user_id_lines, null_user_id_lines, error_logger, errors)
        print("   🔄 Creating contacts validator...")
        validator = ContactsValidator(file_path, None, contacts_headers, delimiter)
        if has_bom:
            validator._cleaned_content = content
    elif headers == points_headers:
        print("   ✅ Detected: POINTS CSV")
        print("   🛠️  Creating points validator...")
        validator = PointsValidator(file_path, None, points_headers, delimiter)
        if has_bom:
            validator._cleaned_content = content
    elif headers == vouchers_headers:
        print("   ✅ Detected: VOUCHERS CSV")
        print("   🛠️  Creating vouchers validator...")
        validator = VoucherValidator(file_path, None, vouchers_headers, delimiter)
        if has_bom:
            validator._cleaned_content = content
    else:
        print("   ❌ Unknown CSV type - headers don't match expected format")
        error_message = generate_error_message(os.path.basename(file_path), headers, contacts_headers, points_headers, vouchers_headers)
        error_logger.log(error_message)
        errors.append(error_message)
        validator = None
    
    print("   🔄 Running detailed validation...")
    validation_result = False
    timestamp_error_count = 0
    
    if validator is not None:
        if processing_mode in ['medium_file', 'large_file']:
            try:
                total_rows = count_file_rows(file_path)
                if total_rows > 1000:
                    colored_print(f"   📊 Processing {total_rows:,} rows with progress tracking...", Colors.CYAN)
                    validator._enable_progress_tracking = True
                    validator._total_rows = total_rows
            except Exception as e:
                print(f"   ⚠️  Could not count rows for progress tracking: {e}")
        
        validation_result = validator.validate()
        
        if hasattr(validator, '_timestamp_error_count'):
            timestamp_error_count = validator._timestamp_error_count
    else:
        print("   ⚠️  No validator available - cannot check content-specific errors")
    
    if errors or not validation_result or timestamp_error_count > 0:
        if validator:
            filename_for_log = getattr(validator, '_original_filename', os.path.basename(file_path))
            

            validation_error_details = validator.validation_error_details + validator.timestamp_error_details
            
            timestamp_errors = [error for error in validation_error_details 
                              if "appears to be in" in error and "format" in error
                              or "should be an integer (UNIX timestamp in milliseconds)" in error]
            timestamp_error_count = len(validator.timestamp_error_details)
            
            validator_error_count = len(validator.validation_error_details)
        else:
            filename_for_log = os.path.basename(file_path)
            validator_error_count = 0
            validation_error_details = []
        
        write_summary_log(error_log_path, filename_for_log, errors, timestamp_error_count, validator_error_count, validation_error_details)
        
        has_bom_error = any("Byte Order Mark (BOM)" in error for error in errors)
        total_errors_found = len(errors) + timestamp_error_count + validator_error_count
        only_bom_error = has_bom_error and total_errors_found == 1
        
        if only_bom_error:
            print("   🔧 BOM is the only error - creating cleaned version for re-validation...")
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            extension = os.path.splitext(os.path.basename(file_path))[1]
            cleaned_filename = f"{base_name}_edited{extension}"
            cleaned_file_path = os.path.join(os.path.dirname(file_path), cleaned_filename)
            
            try:
                with open(cleaned_file_path, 'w', encoding='utf-8') as cleaned_file:
                    cleaned_file.write(content)
                print(f"   ✅ Created cleaned file: {cleaned_filename}")
                
                print("   🔄 Re-validating cleaned file...")
                cleaned_result = classify_csv(cleaned_file_path)
                
                if cleaned_result:
                    print(f"   ✅ Cleaned file validation: SUCCESS")
                    success_path = os.path.join(watch_directory, "success", cleaned_filename)
                    os.rename(cleaned_file_path, success_path)
                else:
                    print(f"   ❌ Cleaned file validation: STILL HAS ERRORS")
                    error_path = os.path.join(watch_directory, "error", cleaned_filename)
                    os.rename(cleaned_file_path, error_path)
                    
            except Exception as e:
                print(f"   ⚠️  Warning: Could not create/validate cleaned file: {e}")
        elif has_bom_error:
            print("   ℹ️  BOM error detected, but other errors also present - no auto-cleanup performed")
        
        if '_temp_corrected.csv' in file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"   ⚠️  Warning: Could not remove temporary file: {e}")
        return False
    
    if '_temp_corrected.csv' in file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"   ⚠️  Warning: Could not remove temporary file: {e}")
        
    return validation_result

def generate_error_message(filename, headers_found, contacts_headers, points_headers, vouchers_headers):
    headers_str = ', '.join(headers_found) if headers_found else "No headers found or file is empty"
    
    detected_type = None
    if headers_found:
        contacts_matches = len(set(headers_found) & set(contacts_headers))
        points_matches = len(set(headers_found) & set(points_headers))
        vouchers_matches = len(set(headers_found) & set(vouchers_headers))
        
        max_matches = max(contacts_matches, points_matches, vouchers_matches)
        if max_matches > 0:
            if contacts_matches == max_matches:
                detected_type = "contacts"
            elif points_matches == max_matches:
                detected_type = "points"
            else:
                detected_type = "vouchers"
    
    if detected_type == "contacts":
        error_msg = f"The header in file {filename} does not match the expected CONTACTS format:\n"
        error_msg += f"\nFound:       {headers_str}"
        error_msg += f"\nExpected:    {', '.join(contacts_headers)}"
    elif detected_type == "points":
        error_msg = f"The header in file {filename} does not match the expected POINTS format:\n"
        error_msg += f"\nFound:       {headers_str}"
        error_msg += f"\nExpected:    {', '.join(points_headers)}"
    elif detected_type == "vouchers":
        error_msg = f"The header in file {filename} does not match the expected VOUCHERS format:\n"
        error_msg += f"\nFound:       {headers_str}"
        error_msg += f"\nExpected:    {', '.join(vouchers_headers)}"
    else:
        error_msg = f"The header in file {filename} does not match any of the expected formats:\n"
        error_msg += f"\nFound:       {headers_str}"
        error_msg += f"\nContacts:    {', '.join(contacts_headers)}"
        error_msg += f"\nPoints:      {', '.join(points_headers)}"
        error_msg += f"\nVouchers:    {', '.join(vouchers_headers)}"
    
    return error_msg

previous_files = process_existing_files()

print()
colored_print("🔍 Now watching for new CSV files... (Press Ctrl+C to stop)", Colors.YELLOW)
colored_print("-" * 60, Colors.CYAN)

try:
    if files_processed:
        timeout_start_time = time.time()
        print()
        colored_print(f"⏰ Auto-completion timer started (10 seconds)", Colors.YELLOW)
    else:
        timeout_start_time = None
    
    while True:
        current_files = set(os.listdir(watch_directory))
        new_files = current_files - previous_files

        for file in new_files:
            if file.endswith(".csv"):
                if '_comma_fixed' in file:
                    colored_print(f"   ⏭️  Skipping auto-generated comma-fixed file: {file}", Colors.CYAN)
                    continue
                    
                full_path = os.path.join(watch_directory, file)
                file_size = os.path.getsize(full_path)
                colored_print(f"\n📄 New file detected: {file}", Colors.BOLD + Colors.BLUE)
                file_size_mb = file_size / (1024 * 1024)
                if file_size_mb >= 1:
                    print(f"   Size: {file_size_mb:.1f} MB ({file_size:,} bytes)")
                else:
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
                    destination = os.path.join(watch_directory, "error", os.path.basename(full_path))
                    try:
                        os.rename(full_path, destination)
                        error_log = os.path.join(watch_directory, "logs", os.path.splitext(os.path.basename(full_path))[0] + ".txt")
                        colored_print(f"   ❌ Status: ERRORS FOUND", Colors.BOLD + Colors.RED)
                        print(f"   📁 Moved to: error/{os.path.basename(full_path)}")
                        print(f"   📋 Error log: logs/{os.path.splitext(os.path.basename(full_path))[0]}.txt")
                        processed_files['error'] += 1
                    except OSError as e:
                        colored_print(f"   ⚠️  Error moving file to error folder: {e}", Colors.RED)
                        processed_files['error'] += 1
                
                files_processed = True
                
                if timeout_start_time is None:
                    timeout_start_time = time.time()
                    print()
                    colored_print(f"⏰ Auto-completion timer started (10 seconds)", Colors.YELLOW)
                
                colored_print("-" * 60, Colors.CYAN)

        previous_files = current_files
        
        if files_processed and timeout_start_time is not None:
            elapsed_time = time.time() - timeout_start_time
            remaining_time = 10 - elapsed_time
            
            if elapsed_time >= 10:
                print()
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
                print(f"\r⏳ Auto-completion in {remaining_time:.1f}s (Ctrl+C to stop early)" + " " * 20, end='\r')
        
        time.sleep(1)

except KeyboardInterrupt:
    print()
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
    print()
    print()
    colored_print(f"💥 Unexpected error occurred: {str(e)}", Colors.BOLD + Colors.RED)
    colored_print("🔄 Please restart the watcher", Colors.YELLOW)
