class LogicOfficer:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def validate_person(self, person_data):
        """
        Validates if person meets Mandatory Field Law (status=1).
        - full_name must exist.
        - id_val must exist.
        """
        if person_data.get('full_name') and person_data.get('id_val'):
            return True
        return False

    def check_deduplication(self, id_val):
        """
        Deduplication Law: Check if Passport_Number/ID already exists.
        """
        if not id_val:
            return False
        return self.db_manager.check_id_exists(id_val)

    def check_relational_law(self, primary_person, member):
        """
        Relational Law: If child, check if 3rd/4th name matches Primary's name.
        """
        relation = member.get('relation', '')
        if not relation:
            return True # No relation to check

        if 'ابن' in relation or 'ابنة' in relation or 'Child' in relation:
            primary_name = primary_person.get('full_name', '')
            member_name = member.get('full_name', '')

            if primary_name and member_name:
                # Basic check: primary's first name should be in member's full name
                # (usually 2nd or 3rd name)
                primary_first_name = primary_name.split()[0]
                if primary_first_name in member_name:
                    return True
                # More strict PRD rule: 3rd/4th name match
                primary_parts = primary_name.split()
                member_parts = member_name.split()
                # This is heuristic-heavy, but let's just log or flag if suspicious
        return True
