# SPDX-FileCopyrightText: 2024 SAP Emarsys
# SPDX-License-Identifier: GPL-3.0-only

import csv
import os
import time
from src.core.logger import Logger

class Validator:
    def __init__(self, csv_path, log_path, expected_columns, delimiter=','):
        self.csv_path = csv_path
        self.delimiter = delimiter
        self.expected_columns = expected_columns
        self.error_logger = Logger(log_path=log_path) if log_path else None
        self._cleaned_content = None
        # Progress tracking attributes
        self._enable_progress_tracking = False
        self._total_rows = 0
        self._processed_rows = 0
        self._start_time = None
        self._last_progress_update = 0
        # Error details storage
        self.validation_error_details = []
        self.timestamp_error_details = []

    def _load_csv(self):
        if hasattr(self, '_cleaned_content') and self._cleaned_content is not None:
            reader = csv.reader(self._cleaned_content.splitlines(), delimiter=self.delimiter, quotechar='"')
            content = [row for row in reader if any(row)]
        else:
            with open(self.csv_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.reader(file, delimiter=self.delimiter, quotechar='"')
                content = [row for row in reader if any(row)]
        return content

    def _update_progress(self, current_row):
        """Update progress display for large files."""
        if not self._enable_progress_tracking:
            return
            
        self._processed_rows = current_row - 1  # Subtract header row
        
        # Update progress every 1000 rows or every 2 seconds
        current_time = time.time()
        should_update = (
            self._processed_rows % 1000 == 0 or 
            current_time - self._last_progress_update >= 2
        )
        
        if should_update and self._total_rows > 0:
            percent = (self._processed_rows / self._total_rows) * 100
            elapsed = current_time - self._start_time
            
            if self._processed_rows > 0:
                rate = self._processed_rows / elapsed
                eta_seconds = (self._total_rows - self._processed_rows) / rate if rate > 0 else 0
                eta_minutes = eta_seconds / 60
                
                if eta_minutes > 1:
                    eta_str = f"ETA: {eta_minutes:.1f}min"
                else:
                    eta_str = f"ETA: {eta_seconds:.0f}sec"
                
                print(f"\r   ⏳ Progress: {self._processed_rows:,}/{self._total_rows:,} ({percent:.1f}%) - {eta_str}", end='', flush=True)
            else:
                print(f"\r   ⏳ Progress: {self._processed_rows:,}/{self._total_rows:,} ({percent:.1f}%)", end='', flush=True)
            
            self._last_progress_update = current_time

    def validate(self):
        # Initialize progress tracking
        if self._enable_progress_tracking:
            self._start_time = time.time()
            print(f"   📊 Starting validation of {self._total_rows:,} rows...")
        
        content = self._load_csv()
        headers = content[0]
        
        has_errors = False
        timestamp_error_rows = []
        error_count = 0
        
        # Memory-efficient error handling - write errors incrementally for large files
        use_streaming_errors = self._enable_progress_tracking and self._total_rows > 10000
        
        for idx, row in enumerate(content[1:], start=2):
            # Update progress for large files
            if self._enable_progress_tracking:
                self._update_progress(idx)
            
            validation_result = self._validate_row(row)
            
            if len(validation_result) == 3:
                is_valid, row_errors, timestamp_errors = validation_result
                if timestamp_errors:
                    timestamp_error_rows.append((idx, row, timestamp_errors))
            else:
                is_valid, row_errors = validation_result
                
            if not is_valid:
                has_errors = True
                error_count += 1
                
                # For large files, write errors immediately to save memory
                if use_streaming_errors:
                    row_error_message = f"Error: {row_errors} -> Row {idx}: {row}"
                    self.validation_error_details.append(row_error_message)
                    if self.error_logger:
                        self.error_logger.log(row_error_message)
                    
                    # Limit memory usage by flushing every 100 errors
                    if error_count % 100 == 0 and self.error_logger:
                        self.error_logger.flush_if_possible()
                else:
                    # Normal processing for smaller files
                    row_error_message = f"Error: {row_errors} -> Row {idx}: {row}"
                    self.validation_error_details.append(row_error_message)
                    if self.error_logger:
                        self.error_logger.log(row_error_message)
        
        # Complete progress tracking
        if self._enable_progress_tracking:
            print(f"\r   ✅ Validation complete: {self._processed_rows:,} rows processed in {time.time() - self._start_time:.1f}s")
        
        # Handle timestamp errors
        if timestamp_error_rows:
            self._timestamp_error_count = len(timestamp_error_rows)
            for idx, row, timestamp_errors in timestamp_error_rows:
                for error in timestamp_errors:
                    timestamp_error_message = f"Error: {error} -> Row {idx}: {row}"
                    self.timestamp_error_details.append(timestamp_error_message)
                    if self.error_logger:
                        self.error_logger.log(timestamp_error_message)
        
        if has_errors:
            if self._enable_progress_tracking:
                print(f"   ⚠️  Found {error_count:,} validation errors")
            return False
        
        return True
    


    def _validate_row(self, values: list[str]) -> tuple[bool, str]:
        if len(values) != len(self.expected_columns):
            return False, f"Row should have {len(self.expected_columns)} columns"
        return True, ""
