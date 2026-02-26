# SPDX-FileCopyrightText: 2024 SAP Emarsys
# SPDX-License-Identifier: GPL-3.0-only

"""Tests for VoucherValidator class."""
import os
import time
import tempfile
import pytest
from src.vouchers.voucher_csv_validator import VoucherValidator


class TestVoucherValidatorRowValidation:
    """Tests for VoucherValidator._validate_row method."""

    @pytest.fixture
    def validator(self, tmp_path):
        """Create a VoucherValidator instance for testing."""
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("userId,externalId,voucherType,voucherName,iconName,code,expiration\n")
        log_path = tmp_path / "errors.log"
        return VoucherValidator(
            csv_path=str(csv_path),
            log_path=str(log_path)
        )

    def _get_future_timestamp(self, days=30):
        """Get a valid future timestamp in milliseconds."""
        return int((time.time() + days * 86400) * 1000)

    def test_valid_row_with_user_id(self, validator):
        """Valid row with userId should pass validation."""
        future_ts = str(self._get_future_timestamp())
        row = ["user123", "", "one_time", "Summer Sale", "basket-colors-1", "SUMMER2024", future_ts]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is True
        assert message == ""
        assert timestamp_errors == []

    def test_valid_row_with_external_id(self, validator):
        """Valid row with externalId should pass validation."""
        future_ts = str(self._get_future_timestamp())
        row = ["", "ext123", "yearly", "Birthday Voucher", "gift-icon", "BDAY2024", future_ts]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is True
        assert message == ""

    def test_missing_both_user_id_and_external_id(self, validator):
        """Row with both userId and externalId empty should fail."""
        future_ts = str(self._get_future_timestamp())
        row = ["", "", "one_time", "Sale", "basket", "CODE123", future_ts]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is False
        assert "userId" in message and "externalId" in message

    def test_invalid_voucher_type(self, validator):
        """Invalid voucherType should fail validation."""
        future_ts = str(self._get_future_timestamp())
        row = ["user123", "", "invalid_type", "Sale", "basket", "CODE123", future_ts]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is False
        assert "voucherType" in message
        assert "one_time" in message or "yearly" in message

    def test_voucher_type_one_time_accepted(self, validator):
        """voucherType 'one_time' should be accepted."""
        future_ts = str(self._get_future_timestamp())
        row = ["user123", "", "one_time", "Sale", "basket", "CODE123", future_ts]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is True

    def test_voucher_type_yearly_accepted(self, validator):
        """voucherType 'yearly' should be accepted."""
        future_ts = str(self._get_future_timestamp())
        row = ["user123", "", "yearly", "Birthday", "gift", "BDAY", future_ts]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is True

    def test_empty_voucher_name(self, validator):
        """Empty voucherName should fail validation."""
        future_ts = str(self._get_future_timestamp())
        row = ["user123", "", "one_time", "", "basket", "CODE123", future_ts]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is False
        assert "voucherName" in message

    def test_empty_icon_name(self, validator):
        """Empty iconName should fail validation."""
        future_ts = str(self._get_future_timestamp())
        row = ["user123", "", "one_time", "Sale", "", "CODE123", future_ts]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is False
        assert "iconName" in message

    def test_empty_code(self, validator):
        """Empty code should fail validation."""
        future_ts = str(self._get_future_timestamp())
        row = ["user123", "", "one_time", "Sale", "basket", "", future_ts]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is False
        assert "code" in message

    def test_expiration_in_seconds_rejected(self, validator):
        """Expiration timestamp in seconds format should be rejected."""
        # Current time in seconds (10 digits)
        seconds_ts = str(int(time.time()) + 86400)
        row = ["user123", "", "one_time", "Sale", "basket", "CODE", seconds_ts]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is False
        assert "seconds" in message.lower()

    def test_expiration_in_past_rejected(self, validator):
        """Expiration timestamp in the past should be rejected."""
        # Timestamp from yesterday
        past_ts = str(int((time.time() - 86400) * 1000))
        row = ["user123", "", "one_time", "Sale", "basket", "CODE", past_ts]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is False
        assert "past" in message.lower()

    def test_expiration_with_decimal_rejected(self, validator):
        """Expiration with decimal point should be rejected."""
        row = ["user123", "", "one_time", "Sale", "basket", "CODE", "1234567890123.45"]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is False
        assert "decimal" in message.lower()

    def test_non_integer_expiration_rejected(self, validator):
        """Non-integer expiration should be rejected."""
        row = ["user123", "", "one_time", "Sale", "basket", "CODE", "not_a_number"]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is False
        assert "integer" in message.lower() or "timestamp" in message.lower()

    def test_wrong_column_count_too_many(self, validator):
        """Row with too many columns should fail with helpful message."""
        future_ts = str(self._get_future_timestamp())
        row = ["user123", "", "one_time", "Sale", "basket", "CODE", future_ts, "extra_field"]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is False
        assert "columns" in message.lower()

    def test_wrong_column_count_too_few(self, validator):
        """Row with too few columns should fail."""
        row = ["user123", "", "one_time", "Sale"]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is False
        assert "columns" in message.lower()

    def test_voucher_name_with_comma_needs_quoting(self, validator):
        """voucherName containing comma should trigger quoting warning."""
        future_ts = str(self._get_future_timestamp())
        row = ["user123", "", "one_time", "Sale, Special Offer", "basket", "CODE", future_ts]
        valid, message, timestamp_errors = validator._validate_row(row)
        assert valid is False
        assert "comma" in message.lower() or "quote" in message.lower()
