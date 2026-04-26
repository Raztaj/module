import sys
import os
from src.database.manager import DatabaseManager
from src.parser.splitter import split_into_people_blocks
from src.parser.extractor import Extractor
from src.parser.logic_officer import LogicOfficer

def process_message(raw_text, db_manager, extractor, logic_officer):
    if not raw_text.strip():
        return
    print(f"\n--- Processing Message ---")
    group_id = db_manager.insert_family_group(raw_text, status=0)

    blocks = split_into_people_blocks(raw_text)

    people_data = []
    for i, block in enumerate(blocks):
        is_primary = (i == 0)
        details = extractor.extract_person_details(block, is_primary=is_primary)
        if not details['full_name'] and not details['id_val']:
            continue
        details['group_id'] = group_id
        people_data.append(details)

    print(f"Extracted {len(people_data)} person records.")

    all_valid = True
    if not people_data:
        all_valid = False

    for person in people_data:
        if logic_officer.check_deduplication(person['id_val']):
            print(f"Warning: ID {person['id_val']} already exists. Skipping.")
            continue

        db_manager.insert_person(person)

        if not logic_officer.validate_person(person):
            all_valid = False
            print(f"Validation Failed: {person.get('full_name') or 'Unknown'}")
        else:
            print(f"Saved: {person['full_name']} (ID: {person['id_val']})")

    status = 1 if all_valid and people_data else 3
    db_manager.update_group_status(group_id, status)
    print(f"Final Status: {'Validated' if status == 1 else 'Error/Incomplete'}")

def main():
    db_manager = DatabaseManager()
    extractor = Extractor()
    logic_officer = LogicOfficer(db_manager)

    print("=== Family Data Orchestrator (Module 1) ===")
    print("Enter/Paste your message(s) below. To finish, type 'EOF' on a new line or press Ctrl+D.")

    lines = []
    try:
        while True:
            line = input()
            if line.strip() == "EOF":
                break
            lines.append(line)
    except EOFError:
        pass

    full_text = "\n".join(lines)

    # Split by the timestamp pattern often seen in the pasted samples if multiple messages are pasted
    import re
    messages = re.split(r'\n(?=\[\d{1,2}:\d{2}\s*[APM]{2},)', full_text)

    if not messages or (len(messages) == 1 and not messages[0].strip()):
        print("No content received.")
        return

    for msg in messages:
        process_message(msg, db_manager, extractor, logic_officer)

    print("\nProcessing complete. Data saved to fdo_data.db")

if __name__ == "__main__":
    main()
