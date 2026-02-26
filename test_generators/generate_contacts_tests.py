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
        "test_files/contacts/valid",
        "test_files/contacts/invalid"
    ]
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)

# Generate timestamps
def get_past_timestamp(days_ago=30):
    past_date = datetime.now() - timedelta(days=days_ago)
    return int(past_date.timestamp() * 1000)  # Convert to milliseconds

def get_future_timestamp(days_ahead=30):
    future_date = datetime.now() + timedelta(days=days_ahead)
    return int(future_date.timestamp() * 1000)  # Convert to milliseconds

past_timestamp = get_past_timestamp()
future_timestamp = get_future_timestamp()

# Define headers
contact_headers = ['userId', 'shouldJoin', 'joinDate', 'tierName', 'tierEntryAt', 'tierCalcAt', 'shouldReward']

# Base valid row template
def get_valid_row(user_id=None):
    if user_id is None:
        user_id = f"user-{int(time.time())}"
    
    return {
        'userId': user_id,
        'shouldJoin': "TRUE",
        'joinDate': str(past_timestamp),
        'tierName': "Gold",
        'tierEntryAt': "",
        'tierCalcAt': "",
        'shouldReward': "TRUE"
    }

# Generate valid files
def generate_valid_files():
    # Valid file with TRUE shouldReward
    with open("test_files/contacts/valid/valid_contacts_reward_true.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=contact_headers)
        writer.writeheader()
        for i in range(1, 11):
            row = get_valid_row(f"user{i}")
            row['shouldReward'] = "TRUE"
            writer.writerow(row)
    
    # Valid file with FALSE shouldReward
    with open("test_files/contacts/valid/valid_contacts_reward_false.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=contact_headers)
        writer.writeheader()
        for i in range(1, 11):
            row = get_valid_row(f"user{i}")
            row['shouldReward'] = "FALSE"
            writer.writerow(row)

# Generate invalid files
def generate_invalid_files():
    # Invalid: Empty userId
    with open("test_files/contacts/invalid/invalid_contacts_empty_userId.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=contact_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row()
        row['userId'] = ""
        writer.writerow(row)
    
    # Invalid: NULL userId
    with open("test_files/contacts/invalid/invalid_contacts_null_userId.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=contact_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row()
        row['userId'] = "NULL"
        writer.writerow(row)
    
    # Invalid: Duplicate userId
    with open("test_files/contacts/invalid/invalid_contacts_duplicate_userId.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=contact_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the duplicate userId
        writer.writerow(get_valid_row("user5"))
    
    # Invalid: shouldJoin not TRUE
    with open("test_files/contacts/invalid/invalid_contacts_shouldJoin_not_true.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=contact_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10")
        row['shouldJoin'] = "FALSE"
        writer.writerow(row)
    
    # Invalid: joinDate in future
    with open("test_files/contacts/invalid/invalid_contacts_future_joinDate.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=contact_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10")
        row['joinDate'] = str(future_timestamp)
        writer.writerow(row)
    
    # Invalid: Non-numeric joinDate
    with open("test_files/contacts/invalid/invalid_contacts_non_numeric_joinDate.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=contact_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10")
        row['joinDate'] = "not-a-timestamp"
        writer.writerow(row)
    
    # Invalid: Non-empty tierEntryAt
    with open("test_files/contacts/invalid/invalid_contacts_non_empty_tierEntryAt.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=contact_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10")
        row['tierEntryAt'] = str(past_timestamp)
        writer.writerow(row)
    
    # Invalid: Non-empty tierCalcAt
    with open("test_files/contacts/invalid/invalid_contacts_non_empty_tierCalcAt.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=contact_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10")
        row['tierCalcAt'] = str(past_timestamp)
        writer.writerow(row)
    
    # Invalid: shouldReward not TRUE or FALSE
    with open("test_files/contacts/invalid/invalid_contacts_invalid_shouldReward.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=contact_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10")
        row['shouldReward'] = "MAYBE"
        writer.writerow(row)

def main():
    create_directories()
    generate_valid_files()
    generate_invalid_files()
    print("Contact test files generated successfully.")

if __name__ == "__main__":
    main()
