from os import environ, listdir
from pyairtable import Table, formulas

auth_token = environ.get('AIRTABLE_API_KEY')
base_id = environ.get('AIRTABLE_BASE_ID')
table_name = environ.get('AIRTABLE_TABLE_NAME', 'Table')


# Returns Airtable table
def airtable_get_table():
    table = Table(auth_token, base_id, table_name)
    return table


# Returns Airtable table data
def airtable_get_table_data():
    table = airtable_get_table()
    data = table.all()
    return data


# Returns Player's Airtable id
def airtable_get_player_id(player_name):
    table = airtable_get_table()
    search_formula = formulas.match({str('full_name'): str(player_name)})
    player_id = table.all(formula=search_formula)[0]['id']
    return player_id


# Returns matching name
def airtable_check_player_name(name):
    # "undefined undefined" comes through from Yahoo
    table = airtable_get_table()
    name_check_jr = name + ' Jr.'  # Ronald Acuna Jr., Vladimir Guerrero Jr.
    name_check_sr = name + ' Sr.'  # Travis Lakins Sr.
    name_check_second = name + ' II'  # Michael Harris II, Cedric Mullins II
    name_check_case = name.lower()  # Ha-seong Kim
    name_check_hypen = name.replace('-', ' ')  # Ji-Hwan Bae, Ji-Man Choi, Hyun-Jin Ryu
    name_check_period = name.replace('.', '')  # A.J. Pollock, D.J. Stewart
    name_check_list = [name, name_check_jr, name_check_sr, name_check_second, name_check_case, name_check_hypen, name_check_period]
    for name_check in name_check_list:
        search_formula = formulas.match({str('full_name'): str(name_check)})
        try:
            # Player name search found result
            name = table.all(formula=search_formula)[0]['fields']['full_name']
            break
        except IndexError:
            # Player name search returned no results, try next name check
            continue
    return name


# Updates Player's Airtable data
def airtable_update_player_data(player_name, player_value, column_name):
    table = airtable_get_table()
    player_id = str(airtable_get_player_id(player_name))
    player_field = {column_name: player_value}
    table.update(player_id, player_field)
    return


# Tests with `pipenv run python src/util_airtable.py`
if __name__ == '__main__':
    print('\n', 'airtable_get_table', '\n', airtable_get_table())
    print('\n', 'airtable_get_table_data', '\n', airtable_get_table_data())
    player_name = 'Ronald Acuna Jr.'
    print('\n', 'airtable_get_player_id()', '\n', airtable_get_player_id(player_name))
    player_value = True
    column_name = 'my_watchlist'
    print('\n', 'airtable_check_player_name()', '\n', airtable_check_player_name(player_name))
    print('\n', 'airtable_update_player_data()', '\n', airtable_update_player_data(player_name, player_value, column_name))
