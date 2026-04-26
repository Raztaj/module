import re

def split_into_people_blocks(text):
    text = text.replace('\r\n', '\n')

    # We want to identify clear person boundaries.
    # Pattern 1: Labels like الاسم, الوالدة, الابنة, ابن, ابنة
    # Pattern 2: Markers like 🔻, *, -, \d+\\

    # Let's use a simpler approach: split by 🔻, *, -, \d+\\ first as they are strong separators.
    lines = text.split('\n')
    blocks = []
    current_block = []

    for line in lines:
        is_sep = False
        # Symbols at start of line
        if re.match(r'^\s*(?:🔻+|\*|\-|•|\d+[\\.)])', line):
            is_sep = True
        # Specific keywords that usually start a new person block
        elif re.match(r'^\s*(?:الاسم|الوالدة|الابنة|المستفيد الرئيسي|لكل فرد من الاسرة)', line):
            is_sep = True

        if is_sep and current_block:
            # Only split if current block has some content
            if len('\n'.join(current_block).strip()) > 10:
                blocks.append('\n'.join(current_block))
                current_block = [line]
            else:
                current_block.append(line)
        else:
            current_block.append(line)

    if current_block:
        blocks.append('\n'.join(current_block))

    return blocks
