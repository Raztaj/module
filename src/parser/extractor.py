import re
from .normalizer import full_normalize
from .date_processor import parse_date

class Extractor:
    def __init__(self):
        self.passport_regex = r'[Pp]\d{7,9}'
        self.unhcr_regex = r'555-\d{2,4}-\d{7,9}|555-\d{7,9}-\d{2,4}|\d{9}-555'

    def extract_phone(self, text):
        potential_phones = re.findall(r'(\+?\d{10,15})', text)
        for phone in potential_phones:
            if (phone.startswith('+20') or phone.startswith('20')) and len(phone) >= 12:
                return phone
            if phone.startswith('01') and len(phone) == 11:
                return phone
        return None

    def extract_id(self, text):
        passport = re.search(self.passport_regex, text)
        if passport: return passport.group(0)
        unhcr = re.search(self.unhcr_regex, text)
        if unhcr: return unhcr.group(0)
        national_id = re.search(r'\b\d{11}\b', text)
        if national_id: return national_id.group(0)
        return None

    def extract_name(self, text):
        # Clean text from timestamps and leading markers
        text = re.sub(r'^\[\d{1,2}:\d{2}\s*[APM]{2},\s*\d{1,2}/\d{1,2}/\d{4}\]\s*\w+:\s*', '', text)
        text = text.lstrip('🔻*•- \n')

        name_labels = ['الاسم رباعي', 'الاسم', 'المستفيد الرئيسي', 'الوالدة', 'الابنة', 'ابن', 'ابنة']

        # Priority 1: Labels
        for label in name_labels:
            match = re.search(rf'{label}\s*[:/]?\s*([^\n\d🔻\*]+)', text)
            if match:
                name = match.group(1).strip().strip('-').strip('*').strip()
                if len(name.split()) >= 2:
                    # Ensure it's not just a status or other field
                    if not any(kw in name for kw in ['متزوج', 'مطلق', 'اعزب', 'طالب', 'جامعي']):
                        return name

        # Priority 2: First line if it looks like a name
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:2]:
            clean_line = re.sub(r'^[🔻\*•\-\d\\.)\s]+', '', line).strip()
            if not re.search(r'\d{5,}', clean_line) and len(clean_line.split()) >= 2:
                if not any(label in clean_line for label in name_labels):
                    # Negative keywords
                    if not any(kw in clean_line for kw in ['متزوج', 'مطلق', 'اعزب', 'طالب', 'جامعي', 'ضغط', 'سكري']):
                        return clean_line

        return None

    def extract_person_details(self, block, is_primary=False):
        normalized_block = full_normalize(block)

        details = {
            'is_primary': is_primary,
            'full_name': self.extract_name(normalized_block),
            'id_val': self.extract_id(normalized_block),
            'phone': self.extract_phone(normalized_block),
            'dob': None,
            'entry_date': None,
            'social_status': self.extract_label_value(normalized_block, ['الحالة الاجتماعية']),
            'health': self.extract_label_value(normalized_block, ['الحالة الصحية']),
            'education': self.extract_label_value(normalized_block, ['المرحلة التعليمية', 'التعليم', 'المراحل التعليمية']),
            'relation': self.extract_label_value(normalized_block, ['صلة القرابة', 'صلة القرابة برب الاسرة'])
        }

        # Date extraction
        dob_match = re.search(r'تاريخ الميلاد\s*[:/]?\s*\n?\s*([^\n]+)', normalized_block)
        if dob_match:
            details['dob'] = parse_date(dob_match.group(1).strip())
        else:
            dates = re.findall(r'(\d{1,2}[/.]\d{1,2}[/.]\d{4})', normalized_block)
            if dates:
                details['dob'] = parse_date(dates[0])

        entry_match = re.search(r'(?:تاريخ دخول مصر|تاريخ الدخول|تاريخ الدخول لمصر)\s*[:/]?\s*\n?\s*([^\n]+)', normalized_block)
        if entry_match:
            details['entry_date'] = parse_date(entry_match.group(1).strip())

        if not details['relation'] and is_primary:
            details['relation'] = 'Primary'

        return details

    def extract_label_value(self, text, labels):
        for label in labels:
            match = re.search(rf'{label}\s*[:/]?\s*([^\n\*🔻-]+)', text)
            if match:
                return match.group(1).strip()
        return None
