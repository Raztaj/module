import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="fdo_data.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS family_groups (
                    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    raw_text TEXT,
                    status INTEGER DEFAULT 0
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS people (
                    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER,
                    is_primary BOOLEAN,
                    full_name TEXT,
                    id_val TEXT,
                    phone TEXT,
                    dob TEXT,
                    entry_date TEXT,
                    social_status TEXT,
                    health TEXT,
                    education TEXT,
                    relation TEXT,
                    FOREIGN KEY (group_id) REFERENCES family_groups (group_id)
                )
            ''')
            conn.commit()

    def insert_family_group(self, raw_text, status=0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO family_groups (raw_text, status) VALUES (?, ?)",
                (raw_text, status)
            )
            return cursor.lastrowid

    def insert_person(self, person_data):
        valid_keys = ['group_id', 'is_primary', 'full_name', 'id_val', 'phone', 'dob', 'entry_date', 'social_status', 'health', 'education', 'relation']
        filtered_data = {k: v for k, v in person_data.items() if k in valid_keys}

        columns = ', '.join(filtered_data.keys())
        placeholders = ', '.join(['?'] * len(filtered_data))
        sql = f"INSERT INTO people ({columns}) VALUES ({placeholders})"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, list(filtered_data.values()))
            return cursor.lastrowid

    def delete_person(self, person_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM people WHERE person_id = ?", (person_id,))
            conn.commit()

    def update_group_status(self, group_id, status):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE family_groups SET status = ? WHERE group_id = ?",
                (status, group_id)
            )

    def get_all_people_by_group(self, group_id):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM people WHERE group_id = ?", (group_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_people_for_export(self):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Joining with family_groups to get status if needed, or just all people
            cursor.execute("SELECT * FROM people")
            return [dict(row) for row in cursor.fetchall()]

    def check_id_exists(self, id_val):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT person_id FROM people WHERE id_val = ?", (id_val,))
            return cursor.fetchone() is not None
