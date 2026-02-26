# SPDX-FileCopyrightText: 2024 SAP Emarsys
# SPDX-License-Identifier: MIT

import os
import csv
import time
from datetime import datetime, timedelta

# Create directory structure
def create_directories():
    # Make sure base test_files directory exists
    os.makedirs("test_files", exist_ok=True)
    
    dirs = [
        "test_files/vouchers/valid",
        "test_files/vouchers/invalid"
    ]
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)

# Generate timestamps
def get_future_timestamp(days_ahead=30):
    future_date = datetime.now() + timedelta(days=days_ahead)
    return int(future_date.timestamp() * 1000)  # Convert to milliseconds

def get_past_timestamp(days_ago=30):
    past_date = datetime.now() - timedelta(days=days_ago)
    return int(past_date.timestamp() * 1000)  # Convert to milliseconds

current_timestamp = int(time.time() * 1000)
future_timestamp = get_future_timestamp()
past_timestamp = get_past_timestamp()

# Define headers
voucher_headers = ['userId', 'externalId', 'voucherType', 'voucherName', 'iconName', 'code', 'expiration']

# Base valid row templates
def get_valid_row(user_id=None, external_id=None, voucher_type="one_time"):
    if user_id is None and external_id is None:
        user_id = "user123"  # Default to ensure at least one ID exists
    
    return {
        'userId': user_id if user_id else "",
        'externalId': external_id if external_id else "",
        'voucherType': voucher_type,
        'voucherName': "10% Discount",
        'iconName': "discount-tag",
        'code': f"DISC{user_id or external_id}-{int(time.time())}",
        'expiration': str(future_timestamp)
    }

# Generate valid files
def generate_valid_files():
    # 1. Valid file with userId only
    with open("test_files/vouchers/valid/valid_vouchers_userId.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=voucher_headers)
        writer.writeheader()
        for i in range(1, 11):
            writer.writerow(get_valid_row(user_id=f"user{i}"))
    
    # 2. Valid file with externalId only
    with open("test_files/vouchers/valid/valid_vouchers_externalId.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=voucher_headers)
        writer.writeheader()
        for i in range(1, 11):
            writer.writerow(get_valid_row(external_id=f"ext{i}"))
    
    # 3. Valid file with both IDs
    with open("test_files/vouchers/valid/valid_vouchers_both_ids.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=voucher_headers)
        writer.writeheader()
        for i in range(1, 11):
            writer.writerow(get_valid_row(user_id=f"user{i}", external_id=f"ext{i}"))
    
    # 4. Valid file with one_time vouchers
    with open("test_files/vouchers/valid/valid_vouchers_one_time.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=voucher_headers)
        writer.writeheader()
        for i in range(1, 11):
            writer.writerow(get_valid_row(user_id=f"user{i}", voucher_type="one_time"))
    
    # 5. Valid file with yearly vouchers
    with open("test_files/vouchers/valid/valid_vouchers_yearly.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=voucher_headers)
        writer.writeheader()
        for i in range(1, 11):
            writer.writerow(get_valid_row(user_id=f"user{i}", voucher_type="yearly"))
    
    # 6. Valid file with mixed voucher types
    with open("test_files/vouchers/valid/valid_vouchers_mixed.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=voucher_headers)
        writer.writeheader()
        for i in range(1, 11):
            voucher_type = "one_time" if i % 2 == 0 else "yearly"
            writer.writerow(get_valid_row(user_id=f"user{i}", voucher_type=voucher_type))

# Generate invalid files
def generate_invalid_files():
    # 1. Invalid: Both userId and externalId empty
    with open("test_files/vouchers/invalid/invalid_vouchers_missing_ids.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=voucher_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(user_id=f"user{i}"))
        # Add the invalid row
        row = get_valid_row(user_id="user10")
        row['userId'] = ""
        row['externalId'] = ""
        writer.writerow(row)
    
    # 2. Invalid: Wrong voucherType
    with open("test_files/vouchers/invalid/invalid_vouchers_wrong_type.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=voucher_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(user_id=f"user{i}"))
        # Add the invalid row
        row = get_valid_row(user_id="user10")
        row['voucherType'] = "monthly"
        writer.writerow(row)
    
    # 3. Invalid: Empty voucherName
    with open("test_files/vouchers/invalid/invalid_vouchers_empty_name.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=voucher_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(user_id=f"user{i}"))
        # Add the invalid row
        row = get_valid_row(user_id="user10")
        row['voucherName'] = ""
        writer.writerow(row)
    
    # 4. Invalid: Empty iconName
    with open("test_files/vouchers/invalid/invalid_vouchers_empty_icon.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=voucher_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(user_id=f"user{i}"))
        # Add the invalid row
        row = get_valid_row(user_id="user10")
        row['iconName'] = ""
        writer.writerow(row)
    
    # 5. Invalid: Empty code
    with open("test_files/vouchers/invalid/invalid_vouchers_empty_code.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=voucher_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(user_id=f"user{i}"))
        # Add the invalid row
        row = get_valid_row(user_id="user10")
        row['code'] = ""
        writer.writerow(row)
    
    # 6. Invalid: Non-numeric expiration
    with open("test_files/vouchers/invalid/invalid_vouchers_invalid_expiration.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=voucher_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(user_id=f"user{i}"))
        # Add the invalid row
        row = get_valid_row(user_id="user10")
        row['expiration'] = "not-a-timestamp"
        writer.writerow(row)
    
    # 7. Invalid: Past expiration
    with open("test_files/vouchers/invalid/invalid_vouchers_past_expiration.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=voucher_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(user_id=f"user{i}"))
        # Add the invalid row
        row = get_valid_row(user_id="user10")
        row['expiration'] = str(past_timestamp)
        writer.writerow(row)

def main():
    create_directories()
    generate_valid_files()
    generate_invalid_files()
    print("Voucher test files generated successfully.")

if __name__ == "__main__":
    main()
