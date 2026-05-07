# SPDX-FileCopyrightText: 2026 SAP Engagement Cloud
# SPDX-License-Identifier: MIT

import os
import sys
import csv
import threading
import webbrowser

# Handle PyInstaller frozen bundle - templates must be found relative to the bundle root
if getattr(sys, 'frozen', False):
    _base_dir = sys._MEIPASS
else:
    _base_dir = os.path.dirname(os.path.abspath(__file__))

from flask import Flask, render_template, request, jsonify
from src.utils.file_utils import detect_encoding, strip_bom, detect_csv_type

app = Flask(__name__, template_folder=os.path.join(_base_dir, 'templates'))

PORT = 7777


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/validate', methods=['POST'])
def validate():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    filename = file.filename or 'upload.csv'

    if not filename.lower().endswith('.csv'):
        return jsonify({
            'filename': filename,
            'csv_type': 'Unknown',
            'row_count': 0,
            'is_valid': False,
            'errors': [{'row': None, 'message': 'Only .csv files are supported'}]
        })

    raw_bytes = file.read()

    if len(raw_bytes) == 0:
        return jsonify({
            'filename': filename,
            'csv_type': 'Unknown',
            'row_count': 0,
            'is_valid': False,
            'errors': [{'row': None, 'message': 'File is empty'}]
        })

    encoding = detect_encoding(raw_bytes)
    content_str = raw_bytes.decode(encoding)

    has_bom = content_str.startswith('﻿')
    content_str = strip_bom(content_str)

    csv_type, validator_class, expected_cols, delimiter = detect_csv_type(content_str)

    file_level_errors = []

    if has_bom:
        file_level_errors.append({'row': None, 'message': 'File starts with a UTF-8 Byte Order Mark (BOM). The BOM has been stripped for validation - remove it from the source file before uploading to SAP Engagement Cloud.'})

    if delimiter == ';':
        file_level_errors.append({'row': None, 'message': 'File uses semicolon (;) separators. SAP Engagement Cloud requires comma (,) separators.'})

    if validator_class is None:
        return jsonify({
            'filename': filename,
            'csv_type': 'Unknown',
            'row_count': 0,
            'is_valid': False,
            'errors': file_level_errors + [{'row': None, 'message': 'Unrecognized CSV format. Headers do not match Contacts, Points, or Vouchers.'}]
        })

    non_empty_lines = [l for l in content_str.splitlines() if l.strip()]
    row_count = max(0, len(non_empty_lines) - 1)

    validator = validator_class('<upload>', None, expected_cols, delimiter)
    validator._cleaned_content = content_str
    validator._enable_progress_tracking = False

    is_valid = validator.validate()

    row_errors = []
    for err in validator.validation_error_details + validator.timestamp_error_details:
        row_num = err['row']
        for msg in err['message'].split('; '):
            msg = msg.strip()
            if msg:
                row_errors.append({'row': row_num, 'message': msg})

    all_errors = file_level_errors + row_errors
    final_valid = is_valid and len(file_level_errors) == 0

    return jsonify({
        'filename': filename,
        'csv_type': csv_type,
        'row_count': row_count,
        'is_valid': final_valid,
        'errors': all_errors
    })


def _open_browser():
    webbrowser.open(f'http://localhost:{PORT}')


if __name__ == '__main__':
    print(f'Loyalty CSV Verifier running at http://localhost:{PORT}')
    print('Press Ctrl+C to stop.')
    threading.Timer(1.0, _open_browser).start()
    app.run(host='127.0.0.1', port=PORT, debug=False)
