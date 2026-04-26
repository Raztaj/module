from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import re
from src.database.manager import DatabaseManager
from src.parser.splitter import split_into_people_blocks
from src.parser.extractor import Extractor
from src.parser.logic_officer import LogicOfficer

app = Flask(__name__)
app.secret_key = "fdo_secret_key"

db_manager = DatabaseManager()
extractor = Extractor()
logic_officer = LogicOfficer(db_manager)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        raw_text = request.form.get('raw_text')
        if not raw_text:
            flash("Please paste some text.", "error")
            return redirect(url_for('index'))

        messages = re.split(r'\n(?=\[\d{1,2}:\d{2}\s*[APM]{2},)', raw_text)

        results = []
        for msg in messages:
            group_id = db_manager.insert_family_group(msg, status=0)
            blocks = split_into_people_blocks(msg)

            people_processed = []
            all_valid = True

            for i, block in enumerate(blocks):
                is_primary = (i == 0)
                details = extractor.extract_person_details(block, is_primary=is_primary)
                if not details['full_name'] and not details['id_val']:
                    continue

                details['group_id'] = group_id

                if logic_officer.check_deduplication(details['id_val']):
                    details['status'] = 'Skipped (Duplicate)'
                    details['person_id'] = None
                else:
                    person_id = db_manager.insert_person(details)
                    details['person_id'] = person_id
                    if not logic_officer.validate_person(details):
                        all_valid = False
                        details['status'] = 'Validation Failed'
                    else:
                        details['status'] = 'Saved'

                people_processed.append(details)

            status = 1 if all_valid and people_processed else 3
            db_manager.update_group_status(group_id, status)
            results.append({'group_id': group_id, 'msg_preview': msg[:50] + '...', 'people': people_processed, 'group_status': status})

        return render_template('results.html', results=results)

    return render_template('index.html')

@app.route('/delete/<int:person_id>', methods=['POST'])
def delete_person(person_id):
    db_manager.delete_person(person_id)
    return jsonify({"status": "success"})

@app.route('/inject/<int:group_id>', methods=['POST'])
def inject_group(group_id):
    # This is a placeholder for Module 2 logic
    # In the future, this will trigger the Playwright automation
    db_manager.update_group_status(group_id, 2) # status=2: Injected
    return jsonify({"status": "success", "message": "Module 2 (Injector) triggered for group " + str(group_id)})

def start_ui():
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    start_ui()
