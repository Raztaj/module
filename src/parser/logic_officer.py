class LogicOfficer:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def validate_person(self, person_data):
        """
        Validates if person meets Mandatory Field Law (status=1).
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
            return True

        if any(kw in relation for kw in ['ابن', 'ابنة', 'Child']):
            primary_name = primary_person.get('full_name', '')
            member_name = member.get('full_name', '')

            if primary_name and member_name:
                primary_parts = primary_name.split()
                member_parts = member_name.split()

                # Rule: Primary's first name should be child's 2nd, 3rd, or 4th name
                primary_first = primary_parts[0]
                # Check child's names from index 1 onwards
                if primary_first in member_parts[1:]:
                    return True
                return False
        return True
