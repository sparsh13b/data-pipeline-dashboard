"""
test_clean_data.py
unit tests for the data cleaning functions.
run with: python -m pytest tests/ -v
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# add parent dir to path so we can import clean_data
sys.path.insert(0, str(Path(__file__).parent.parent))

from clean_data import parse_date, validate_email, normalize_status


# ---- date parsing tests ----

class TestParseDate:
    def test_standard_format(self):
        result = parse_date("2024-03-15")
        assert result == pd.Timestamp("2024-03-15")

    def test_dd_mm_yyyy(self):
        result = parse_date("15/03/2024")
        assert result == pd.Timestamp("2024-03-15")

    def test_mm_dd_yyyy(self):
        result = parse_date("03-15-2024")
        assert result == pd.Timestamp("2024-03-15")

    def test_invalid_date(self):
        result = parse_date("not-a-date")
        assert pd.isna(result)

    def test_empty_string(self):
        result = parse_date("")
        assert pd.isna(result)

    def test_none_value(self):
        result = parse_date(None)
        assert pd.isna(result)


# ---- email validation tests ----

class TestValidateEmail:
    def test_valid_email(self):
        assert validate_email("test@example.com") == True

    def test_missing_at(self):
        assert validate_email("testexample.com") == False

    def test_missing_dot(self):
        assert validate_email("test@examplecom") == False

    def test_empty_email(self):
        assert validate_email("") == False

    def test_none_email(self):
        assert validate_email(None) == False

    def test_uppercase_valid(self):
        # uppercase but still valid format
        assert validate_email("TEST@EXAMPLE.COM") == True


# ---- status normalization tests ----

class TestNormalizeStatus:
    def test_already_correct(self):
        assert normalize_status("completed") == "completed"

    def test_done_maps_to_completed(self):
        assert normalize_status("done") == "completed"

    def test_canceled_maps_to_cancelled(self):
        assert normalize_status("canceled") == "cancelled"

    def test_uppercase(self):
        assert normalize_status("COMPLETED") == "completed"

    def test_mixed_case(self):
        assert normalize_status("Pending") == "pending"

    def test_refund_maps_to_refunded(self):
        assert normalize_status("refund") == "refunded"

    def test_none_returns_none(self):
        result = normalize_status(None)
        assert result is None
