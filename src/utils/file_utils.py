# SPDX-FileCopyrightText: 2026 SAP Engagement Cloud
# SPDX-License-Identifier: MIT

import csv

CONTACTS_HEADERS = ["userId", "shouldJoin", "joinDate", "tierName", "tierEntryAt", "tierCalcAt", "shouldReward"]
POINTS_HEADERS = ["userId", "pointsToSpend", "statusPoints", "cashback", "allocatedAt", "expireAt", "setPlanExpiration", "reason", "title", "description"]
VOUCHERS_HEADERS = ["userId", "externalId", "voucherType", "voucherName", "iconName", "code", "expiration"]


def detect_encoding(raw_bytes):
    try:
        raw_bytes.decode('utf-8')
        return 'utf-8'
    except UnicodeDecodeError:
        return 'ISO-8859-1'


def strip_bom(content):
    if content.startswith('﻿'):
        return content[1:]
    return content


def detect_csv_type(content_str):
    from src.contacts.contacts_csv_validator import ContactsValidator
    from src.points.points_csv_validator import PointsValidator
    from src.vouchers.voucher_csv_validator import VoucherValidator

    _type_map = {
        tuple(CONTACTS_HEADERS): ("Contacts", ContactsValidator, CONTACTS_HEADERS),
        tuple(POINTS_HEADERS): ("Points", PointsValidator, POINTS_HEADERS),
        tuple(VOUCHERS_HEADERS): ("Vouchers", VoucherValidator, VOUCHERS_HEADERS),
    }

    content_lines = content_str.splitlines()
    for delimiter in (',', ';'):
        reader = csv.DictReader(content_lines, delimiter=delimiter)
        headers = reader.fieldnames
        if headers:
            key = tuple(headers)
            if key in _type_map:
                csv_type, validator_class, expected_cols = _type_map[key]
                return csv_type, validator_class, expected_cols, delimiter

    return "Unknown", None, [], ','
