import pytest
from src.parser.normalizer import full_normalize
from src.parser.date_processor import parse_date
from src.parser.extractor import Extractor

def test_normalization():
    assert full_normalize("١٢٣") == "123"
    assert full_normalize("إأآ") == "ااا"
    assert full_normalize("ى") == "ي"

def test_date_parsing():
    assert parse_date("28 ديسمبر 1986") == "1986-12-28"
    assert parse_date("1/1/1975") == "1975-01-01"
    assert parse_date("30.5.2005") == "2005-05-30"

def test_extraction():
    extractor = Extractor()
    sample = """رقم الهوية /11501530764
رقم الهاتف/01124253177
تاريخ الميلاد / 28 ديسمبر 1986
تاريخ دخول مصر / 23يوليو 2023"""
    details = extractor.extract_person_details(sample, is_primary=True)
    assert details['id_val'] == "11501530764"
    assert details['phone'] == "01124253177"
    assert details['dob'] == "1986-12-28"
    assert details['entry_date'] == "2023-07-23"

def test_egyptian_phone_filter():
    extractor = Extractor()
    # Sudanese number
    assert extractor.extract_phone("249912607626+") is None
    # Egyptian number
    assert extractor.extract_phone("01050771560") == "01050771560"
    assert extractor.extract_phone("+201050771560") == "+201050771560"
