from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import os
import re
import pandas as pd
import io
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
            primary_person = None

            for i, block in enumerate(blocks):
                is_primary = (i == 0)
                details = extractor.extract_person_details(block, is_primary=is_primary)
                if not details['full_name'] and not details['id_val']:
                    continue

                details['group_id'] = group_id
                if is_primary:
                    primary_person = details

                if logic_officer.check_deduplication(details['id_val']):
                    details['status'] = 'Skipped (Duplicate)'
                    details['person_id'] = None
                else:
                    person_id = db_manager.insert_person(details)
                    details['person_id'] = person_id

                    # Validation
                    valid = logic_officer.validate_person(details)
                    relational_valid = True
                    if not is_primary and primary_person:
                        relational_valid = logic_officer.check_relational_law(primary_person, details)

                    details['relational_error'] = not relational_valid

                    if not valid:
                        details['status'] = 'Validation Failed'
                    elif not relational_valid:
                        details['status'] = 'Relational Warning'
                    else:
                        details['status'] = 'Saved'

                people_processed.append(details)

            all_valid = all(p.get('status') == 'Saved' for p in people_processed)
            status = 1 if all_valid and people_processed else 3
            db_manager.update_group_status(group_id, status)
            results.append({'group_id': group_id, 'msg_preview': msg[:50] + '...', 'people': people_processed, 'group_status': status})

        return render_template('results.html', results=results)

    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    groups = db_manager.get_all_groups()
    return render_template('dashboard.html', groups=groups)

@app.route('/group/<int:group_id>')
def view_group(group_id):
    people = db_manager.get_all_people_by_group(group_id)
    return render_template('results.html', results=[{'group_id': group_id, 'msg_preview': 'Group #' + str(group_id), 'people': people, 'group_status': None}])

@app.route('/update/<int:person_id>', methods=['POST'])
def update_person(person_id):
    data = request.json
    db_manager.update_person(person_id, data)
    return jsonify({"status": "success"})

@app.route('/delete/<int:person_id>', methods=['POST'])
def delete_person(person_id):
    db_manager.delete_person(person_id)
    return jsonify({"status": "success"})

@app.route('/inject/<int:group_id>', methods=['POST'])
def inject_group(group_id):
    db_manager.update_group_status(group_id, 2)
    return jsonify({"status": "success", "message": "Module 2 (Injector) triggered for group " + str(group_id)})

@app.route('/export')
def export_excel():
    people = db_manager.get_all_people_for_export()
    if not people:
        flash("No data to export.", "error")
        return redirect(url_for('index'))
    df = pd.DataFrame(people)
    cols = ['person_id', 'group_id', 'full_name', 'id_val', 'phone', 'dob', 'entry_date', 'relation', 'social_status', 'health', 'education']
    df = df[[c for c in cols if c in df.columns]]
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='People')
    output.seek(0)
    return send_file(output, download_name="fdo_export.xlsx", as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def start_ui():
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    start_ui()
