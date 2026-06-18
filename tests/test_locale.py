import pytest
from stages.locale import extract_locale, validate_locale_format, check_canonical_locale

def test_extract_locale_valid():
    url = "https://www.example.com/US/en/product/test"
    locale = extract_locale(url)

    assert locale == {"country": "US", "language": "en"}

def test_extract_locale_invalid():
    url = "https://www.example.com/product/test"
    locale = extract_locale(url)

    assert locale is None

def test_validate_locale_format_valid():
    is_valid = validate_locale_format("US", "en")
    assert is_valid is True

def test_validate_locale_format_invalid_country():
    is_valid = validate_locale_format("USA", "en")
    assert is_valid is False

def test_validate_locale_format_invalid_language():
    is_valid = validate_locale_format("US", "english")
    assert is_valid is False

def test_check_canonical_locale():
    url = "https://www.example.com/US/en/product/test"
    canonical = "https://www.example.com/US/en/product/test"

    matches = check_canonical_locale(url, canonical)
    assert matches is True

def test_check_canonical_locale_mismatch():
    url = "https://www.example.com/US/en/product/test"
    canonical = "https://www.example.com/UK/en/product/test"

    matches = check_canonical_locale(url, canonical)
    assert matches is False

def test_extract_locale_variations():
    # Test different valid patterns
    urls = [
        "https://example.com/US/en/product/test",
        "https://example.com/GB/en/product/test",
        "https://example.com/DE/de/product/test",
        "https://example.com/FR/fr/product/test"
    ]

    for url in urls:
        locale = extract_locale(url)
        assert locale is not None
        assert len(locale["country"]) == 2
        assert len(locale["language"]) == 2
