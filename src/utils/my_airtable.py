from os import environ
from pyairtable import Table

# Returns Airtable Base Table
def get_table():
    auth_token = environ.get('AIRTABLE_API_KEY')
    base_id = environ.get('AIRTABLE_BASE_ID')
    table_name = 'Table'
    table = Table(auth_token, base_id, table_name)
    return table.all()

# Used for testing with `pipenv run python src/utils/my_airtable.py`
if __name__ == "__main__":
    print('\n', 'get_table', '\n', get_table())
