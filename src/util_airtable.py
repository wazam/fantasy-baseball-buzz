from os import environ
from pyairtable import Table

auth_token = environ.get('AIRTABLE_API_KEY')
base_id = environ.get('AIRTABLE_BASE_ID')
table_name = environ.get('AIRTABLE_TABLE_NAME', 'Table')


# Returns Airtable Base Table
def airtable_get_table():
    table = Table(auth_token, base_id, table_name)
    return table.all()


# Tests with `pipenv run python src/util_airtable.py`
if __name__ == '__main__':
    print('\n', 'airtable_get_table', '\n', airtable_get_table())
