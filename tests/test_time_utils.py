# SPDX-FileCopyrightText: 2024 SAP Emarsys
# SPDX-License-Identifier: MIT

"""Tests for time_utils module."""
import time
import pytest
from src.utils.time_utils import (
    FROM_DATE,
    TILL_DATE,
    _is_unix_millisecond_timestamp,
    _is_past_timestamp,
    _has_decimal_separators,
    _needs_csv_quoting,
)


class TestDateConstants:
    """Tests for FROM_DATE and TILL_DATE constants."""

    def test_from_date_is_correct_value(self):
        """FROM_DATE should be Jan 2, 1970 00:00:00 UTC in milliseconds."""
        # 86400 seconds = 1 day after epoch
        expected = 86400 * 1000  # 86400000 ms
        assert FROM_DATE == expected

    def test_till_date_is_correct_value(self):
        """TILL_DATE should be Jan 1, 2100 00:00:00 UTC in milliseconds."""
        # Known value for 2100-01-01 00:00:00 UTC
        expected = 4102444800 * 1000  # 4102444800000 ms
        assert TILL_DATE == expected

    def test_from_date_is_positive(self):
        """FROM_DATE must be a positive number."""
        assert FROM_DATE > 0

    def test_till_date_is_after_from_date(self):
        """TILL_DATE must be after FROM_DATE."""
        assert TILL_DATE > FROM_DATE


class TestIsUnixMillisecondTimestamp:
    """Tests for _is_unix_millisecond_timestamp function."""

    def test_negative_timestamp_rejected(self):
        """Negative timestamps should be rejected."""
        valid, message = _is_unix_millisecond_timestamp(-1)
        assert valid is False
        assert "negative" in message.lower()

    def test_seconds_format_rejected(self):
        """Timestamps in seconds format (10 digits) should be rejected."""
        # Current time in seconds
        timestamp_seconds = int(time.time())
        valid, message = _is_unix_millisecond_timestamp(timestamp_seconds)
        assert valid is False
        assert "seconds" in message.lower()

    def test_valid_millisecond_timestamp_accepted(self):
        """Valid 13-digit millisecond timestamps should be accepted."""
        # Current time in milliseconds
        timestamp_millis = int(time.time() * 1000)
        valid, message = _is_unix_millisecond_timestamp(timestamp_millis)
        assert valid is True

    def test_microseconds_format_rejected(self):
        """Timestamps in microseconds format (16 digits) should be rejected."""
        timestamp_micros = int(time.time() * 1000000)
        valid, message = _is_unix_millisecond_timestamp(timestamp_micros)
        assert valid is False
        assert "microseconds" in message.lower()

    def test_nanoseconds_format_rejected(self):
        """Timestamps in nanoseconds format (19 digits) should be rejected."""
        timestamp_nanos = int(time.time() * 1000000000)
        valid, message = _is_unix_millisecond_timestamp(timestamp_nanos)
        assert valid is False
        assert "nanoseconds" in message.lower()

    def test_truncated_milliseconds_rejected(self):
        """12-digit timestamps (truncated milliseconds) should be rejected."""
        truncated = 123456789012  # 12 digits
        valid, message = _is_unix_millisecond_timestamp(truncated)
        assert valid is False
        assert "truncated" in message.lower()

    def test_small_value_rejected(self):
        """Very small values should be rejected with appropriate message."""
        valid, message = _is_unix_millisecond_timestamp(12345)
        assert valid is False
        assert "minutes/hours" in message.lower() or "digits" in message.lower()

    def test_timestamp_before_range_rejected(self):
        """Timestamps before 1970-01-02 should be rejected."""
        # 1 ms after epoch - before FROM_DATE
        valid, message = _is_unix_millisecond_timestamp(1)
        assert valid is False

    def test_timestamp_after_range_rejected(self):
        """Timestamps after 2100-01-01 should be rejected."""
        # Far future: year 2150
        far_future = 5000000000000  # Beyond 2100
        valid, message = _is_unix_millisecond_timestamp(far_future)
        assert valid is False
        assert "outside valid date range" in message.lower()

    def test_minimum_valid_13_digit_timestamp_accepted(self):
        """Minimum valid 13-digit timestamp within range should be accepted."""
        # First 13-digit number that's >= FROM_DATE
        min_valid = 1000000000000  # Year 2001
        valid, message = _is_unix_millisecond_timestamp(min_valid)
        assert valid is True

    def test_just_before_till_date_accepted(self):
        """Timestamp just before TILL_DATE should be accepted."""
        valid, message = _is_unix_millisecond_timestamp(int(TILL_DATE) - 1)
        assert valid is True


class TestIsPastTimestamp:
    """Tests for _is_past_timestamp function."""

    def test_past_timestamp_detected(self):
        """Timestamps in the past should be detected."""
        past_timestamp = int(time.time() * 1000) - 60000  # 1 minute ago
        is_past, message = _is_past_timestamp(past_timestamp)
        assert is_past is True
        assert "past" in message.lower()

    def test_future_timestamp_not_past(self):
        """Timestamps in the future should not be marked as past."""
        future_timestamp = int(time.time() * 1000) + 60000  # 1 minute from now
        is_past, message = _is_past_timestamp(future_timestamp)
        assert is_past is False


class TestHasDecimalSeparators:
    """Tests for _has_decimal_separators function."""

    def test_empty_value_no_decimal(self):
        """Empty string should not have decimal separator."""
        has_decimal, message = _has_decimal_separators("")
        assert has_decimal is False

    def test_none_value_no_decimal(self):
        """None value should not have decimal separator."""
        has_decimal, message = _has_decimal_separators(None)
        assert has_decimal is False

    def test_comma_decimal_detected(self):
        """Comma used as decimal separator should be detected."""
        has_decimal, message = _has_decimal_separators("123,45")
        assert has_decimal is True
        assert "comma" in message.lower()

    def test_period_decimal_detected(self):
        """Period used as decimal separator should be detected."""
        has_decimal, message = _has_decimal_separators("123.45")
        assert has_decimal is True
        assert "decimal point" in message.lower()

    def test_integer_string_no_decimal(self):
        """Plain integer string should not have decimal separator."""
        has_decimal, message = _has_decimal_separators("12345")
        assert has_decimal is False

    def test_multiple_commas_not_decimal(self):
        """Multiple commas (thousand separators) should not be flagged as decimal."""
        has_decimal, message = _has_decimal_separators("1,234,567")
        assert has_decimal is False


class TestNeedsCsvQuoting:
    """Tests for _needs_csv_quoting function."""

    def test_empty_value_no_quoting(self):
        """Empty string should not need quoting."""
        needs_quoting, message = _needs_csv_quoting("")
        assert needs_quoting is False

    def test_none_value_no_quoting(self):
        """None value should not need quoting."""
        needs_quoting, message = _needs_csv_quoting(None)
        assert needs_quoting is False

    def test_value_with_comma_needs_quoting(self):
        """Values containing commas should need quoting."""
        needs_quoting, message = _needs_csv_quoting("Hello, World")
        assert needs_quoting is True
        assert "commas" in message.lower()

    def test_value_without_comma_no_quoting(self):
        """Values without commas should not need quoting."""
        needs_quoting, message = _needs_csv_quoting("Hello World")
        assert needs_quoting is False
