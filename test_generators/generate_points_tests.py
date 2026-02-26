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
        "test_files/points/valid",
        "test_files/points/invalid"
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
allocated_at_timestamp = past_timestamp - 10000000  # Earlier than expiration

# Define headers
points_headers = ["userId", "pointsToSpend", "statusPoints", "cashback", "allocatedAt", 
                 "expireAt", "setPlanExpiration", "reason", "title", "description"]

# Base valid row template
def get_valid_row(user_id=None, points_to_spend="100", status_points="50", cashback="10.5", 
                 set_plan_expiration="FALSE"):
    if user_id is None:
        user_id = f"user-{int(time.time())}"
    
    expireAt = str(future_timestamp) if set_plan_expiration.upper() == "FALSE" else ""
    
    return {
        'userId': user_id,
        'pointsToSpend': points_to_spend,
        'statusPoints': status_points,
        'cashback': cashback,
        'allocatedAt': str(allocated_at_timestamp),
        'expireAt': expireAt,
        'setPlanExpiration': set_plan_expiration,
        'reason': "Welcome bonus",
        'title': "Welcome Points",
        'description': "Points awarded for signing up"
    }

# Generate valid files
def generate_valid_files():
    # Valid file with setPlanExpiration=FALSE
    with open("test_files/points/valid/valid_points_plan_false.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 11):
            writer.writerow(get_valid_row(f"user{i}", set_plan_expiration="FALSE"))
    
    # Valid file with setPlanExpiration=TRUE
    with open("test_files/points/valid/valid_points_plan_true.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 11):
            writer.writerow(get_valid_row(f"user{i}", set_plan_expiration="TRUE"))
    
    # Valid file with only pointsToSpend
    with open("test_files/points/valid/valid_points_only_spend.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 11):
            writer.writerow(get_valid_row(f"user{i}", points_to_spend="100", status_points="0", cashback="0"))
    
    # Valid file with only statusPoints
    with open("test_files/points/valid/valid_points_only_status.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 11):
            writer.writerow(get_valid_row(f"user{i}", points_to_spend="0", status_points="50", cashback="0"))
    
    # Valid file with only cashback
    with open("test_files/points/valid/valid_points_only_cashback.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 11):
            writer.writerow(get_valid_row(f"user{i}", points_to_spend="0", status_points="0", cashback="10.5"))

# Generate invalid files
def generate_invalid_files():
    # Invalid: Non-positive values in all points fields
    with open("test_files/points/invalid/invalid_points_no_positive_values.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10", points_to_spend="0", status_points="0", cashback="0")
        writer.writerow(row)
    
    # Invalid: Non-numeric pointsToSpend
    with open("test_files/points/invalid/invalid_points_non_numeric_pointsToSpend.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10")
        row['pointsToSpend'] = "abc"
        writer.writerow(row)
    
    # Invalid: Non-numeric statusPoints
    with open("test_files/points/invalid/invalid_points_non_numeric_statusPoints.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10")
        row['statusPoints'] = "abc"
        writer.writerow(row)
    
    # Invalid: Non-numeric cashback
    with open("test_files/points/invalid/invalid_points_non_numeric_cashback.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10")
        row['cashback'] = "abc"
        writer.writerow(row)
    
    # Invalid: setPlanExpiration=TRUE with non-empty expireAt
    with open("test_files/points/invalid/invalid_points_plan_true_with_expireAt.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10", set_plan_expiration="TRUE")
        row['expireAt'] = str(future_timestamp)
        writer.writerow(row)
    
    # Invalid: setPlanExpiration=FALSE with empty expireAt
    with open("test_files/points/invalid/invalid_points_plan_false_without_expireAt.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10", set_plan_expiration="FALSE")
        row['expireAt'] = ""
        writer.writerow(row)
    
    # Invalid: setPlanExpiration=FALSE with past expireAt
    with open("test_files/points/invalid/invalid_points_past_expireAt.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10", set_plan_expiration="FALSE")
        row['expireAt'] = str(past_timestamp)
        writer.writerow(row)
    
    # Invalid: setPlanExpiration invalid value
    with open("test_files/points/invalid/invalid_points_invalid_setPlanExpiration.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10")
        row['setPlanExpiration'] = "MAYBE"
        writer.writerow(row)
    
    # Invalid: Negative value in points
    with open("test_files/points/invalid/invalid_points_negative_value.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=points_headers)
        writer.writeheader()
        for i in range(1, 10):
            writer.writerow(get_valid_row(f"user{i}"))
        # Add the invalid row
        row = get_valid_row("user10")
        row['pointsToSpend'] = "-10"
        writer.writerow(row)

def main():
    create_directories()
    generate_valid_files()
    generate_invalid_files()
    print("Points test files generated successfully.")

if __name__ == "__main__":
    main()
