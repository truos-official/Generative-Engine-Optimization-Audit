"""Locale validation logic."""

import re


def extract_locale(url: str) -> dict[str, str] | None:
    """Extract locale (country/language) from URL."""
    # Pattern: /COUNTRY/LANG/
    pattern = r'/([A-Z]{2})/([a-z]{2})/'
    match = re.search(pattern, url)

    if match:
        return {
            "country": match.group(1),
            "language": match.group(2)
        }

    return None


def validate_locale_format(country: str, language: str) -> bool:
    """Validate locale format (2-letter codes)."""
    if len(country) != 2 or not country.isupper():
        return False

    if len(language) != 2 or not language.islower():
        return False

    return True


def check_canonical_locale(url: str, canonical_url: str) -> bool:
    """Check if URL locale matches canonical URL locale."""
    url_locale = extract_locale(url)
    canonical_locale = extract_locale(canonical_url)

    if url_locale is None and canonical_locale is None:
        return True

    if url_locale is None or canonical_locale is None:
        return False

    return (url_locale["country"] == canonical_locale["country"] and
            url_locale["language"] == canonical_locale["language"])
