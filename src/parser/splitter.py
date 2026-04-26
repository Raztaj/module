import re

def split_into_people_blocks(text):
    """
    Splits a message into separate blocks, each representing one person.
    Improved to handle (رب الاسره), (ابنه), (ابن) and double newlines.
    """
    text = text.replace('\r\n', '\n')

    # Heuristic 1: Split on double newlines as a strong indicator of record separation
    raw_blocks = re.split(r'\n\s*\n', text)

    # Heuristic 2: Further split if a block contains multiple person markers
    # markers indicate a NEW person starts
    markers = [
        r'🔻+',
        r'^\s*\* ',
        r'^\s*\- ',
        r'^\s*\d+[\\.)]',
        r'الاسم\s*[/:]',
        r'الوالدة\s*[/:]',
        r'الابنة\s*[/:]',
        r'المستفيد الرئيسي',
        r'لكل فرد من الاسرة',
        r'\(رب الاسره\)', # Added
        r'\(ابنه\)', # Added
        r'\(ابن\)', # Added
        r'\(زوجه\)', # Added
    ]

    final_blocks = []
    for raw_block in raw_blocks:
        lines = raw_block.split('\n')
        current_sub_block = []
        for line in lines:
            is_new = False
            if any(re.search(m, line) for m in markers):
                if "عدد افراد الاسرة" not in line and "عدد أفراد الأسرة" not in line:
                    is_new = True

            if is_new and current_sub_block:
                final_blocks.append('\n'.join(current_sub_block))
                current_sub_block = [line]
            else:
                current_sub_block.append(line)
        if current_sub_block:
            final_blocks.append('\n'.join(current_sub_block))

    return [b for b in final_blocks if len(b.strip()) > 10]
