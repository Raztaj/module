import re

def parse_date(date_str):
    r"""
    Parses various Arabic and Western date formats into ISO YYYY-MM-DD.
    Formats handled:
    - DD/MM/YYYY
    - DD.MM.YYYY
    - DD\MM\YYYY
    - DD Month Name YYYY
    """
    if not date_str:
        return None

    # Normalize separators
    date_str = date_str.replace('.', '/').replace('\\', '/').strip()

    arabic_months = {
        'يناير': '01', 'فبراير': '02', 'مارس': '03', 'ابريل': '04',
        'مايو': '05', 'يونيو': '06', 'يوليو': '07', 'اغسطس': '08',
        'سبتمبر': '09', 'اكتوبر': '10', 'نوفمبر': '11', 'ديسمبر': '12'
    }

    # Try DD/MM/YYYY
    match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
    if match:
        d, m, y = match.groups()
        return f"{y}-{m.zfill(2)}-{d.zfill(2)}"

    # Try YYYY/MM/DD
    match = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_str)
    if match:
        y, m, d = match.groups()
        return f"{y}-{m.zfill(2)}-{d.zfill(2)}"

    # Try DD Month Name YYYY
    for month_name, month_num in arabic_months.items():
        if month_name in date_str:
            match = re.search(rf'(\d{{1,2}})\s*{month_name}\s*(\d{{4}})', date_str)
            if match:
                d, y = match.groups()
                return f"{y}-{month_num}-{d.zfill(2)}"

    return date_str
