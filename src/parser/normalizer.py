import re

def normalize_numbers(text):
    """Converts Eastern Arabic numerals to Western Arabic numerals."""
    eastern_to_western = {
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
    }
    for e, w in eastern_to_western.items():
        text = text.replace(e, w)
    return text

def normalize_arabic_text(text):
    """Standardizes Hamzas, Ya, and strips Tashkeel."""
    # Strip Tashkeel
    tashkeel_pattern = re.compile(r'[\u064B-\u0652]')
    text = re.sub(tashkeel_pattern, '', text)

    # Normalize Hamzas
    text = re.sub(r'[إأآ]', 'ا', text)

    # Normalize Ya/Alef Maksura
    text = re.sub(r'ى', 'ي', text)

    return text

def full_normalize(text):
    if not text:
        return ""
    text = normalize_numbers(text)
    text = normalize_arabic_text(text)
    return text
