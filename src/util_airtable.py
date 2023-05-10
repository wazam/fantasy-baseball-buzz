from os import environ
from time import sleep
from pyairtable import Table, formulas
from requests.exceptions import HTTPError, ConnectionError

auth_token = environ.get('AIRTABLE_API_KEY')
base_id = environ.get('AIRTABLE_BASE_ID')
table_name = environ.get('AIRTABLE_TABLE_NAME')

# Returns Airtable table
def airtable_setup():
    table = Table(auth_token, base_id, table_name)
    return table


# Returns Player's Airtable ID (team/position lookup only used for players with exact same name)
def airtable_get_player_id(name, team, position):
    table = airtable_setup()
    player_found = False
    name_check_jr = name + ' Jr.'  # Ronald Acuna Jr., Vladimir Guerrero Jr.
    name_check_sr = name + ' Sr.'  # Travis Lakins Sr.
    name_check_second = name + ' II'  # Michael Harris II, Cedric Mullins II
    name_check_case = name.title()  # Ha-seong Kim, sAMUEL Infante
    name_check_hypen = name.replace('-', ' ')  # Ji-Hwan Bae, Ji-Man Choi, Hyun-Jin Ryu
    name_check_period = name.replace('.', '')  # A.J. Pollock, D.J. Stewart
    name_intials = [x[0] for x in name.split("-")]
    name_check_initials = ''
    try:
        name_check_initials = str(name_intials[0] + "." + name_intials[1] + ". " + name.split()[-1])  # Jean-Carlos Mejia (Y!) -> J.C. Mejia (ESPN)
    except IndexError:
        pass
    name_check_list_full = [name, name_check_jr, name_check_sr, name_check_second, name_check_case, name_check_hypen, name_check_period]
    if name_check_initials != '':
        name_check_list_full.append(name_check_initials)
    # name_check_list = [*set(name_check_list_full)]
    for name_check in name_check_list_full:
        search_formula = formulas.match({'Player': str(name_check)})
        search_results = table.all(formula=search_formula)
        number_of_players = len(search_results)
        # Loop through each player in the search results
        for player in range(0, number_of_players):
            player_team = search_results[player]['fields']['Team']
            # If the team matches, its a match 99.99% of the time
            if player_team == team:
                # Manual fix for two 'Josh Smith' players both on the Texas Rangers as of 2023-05-08
                if player_team == 'Tex':
                    player_posititon = search_results[player]['fields']['Position']
                    if player_posititon == position:
                        # player_name = search_results[player]['fields']['Player']
                        player_id = search_results[player]['id']
                        player_found = True
                        break
                else:
                    player_id = search_results[player]['id']
                    player_found = True
                    break
        if player_found == True:
            break
    if player_found != True:
        # No Name(+check) & Team combination found in search results
        return False
    return player_id


# Creates row for new Player in table if it does not exist
def airtable_check_and_create_player(name, team, position):
    if airtable_get_player_id(name, team, position) == False:
        table = airtable_setup()
        fields = {'Player': name, 'Team': team, 'Position': position, 'New': True}
        table.create(fields)
    return


# Updates data in one column for Player
def airtable_update_player_data(name, team, position, column, value):
    table = airtable_setup()
    id = str(airtable_get_player_id(name, team, position))
    field = {str(column): value}
    table.update(id, field)
    return


# Updates Player's data in batch from list of records
def airtable_batch_update_player_data(records):
    table = airtable_setup()
    # example_list_of_records = [{"id": "recwPQIfs4wKPyc9D", "fields": {"First Name": "Matt", ...}}, {"id": ...]
    try:
        table.batch_update(records)
    except (HTTPError, ConnectionError) as error:
        print(error)
        sleep(30)
        table.batch_update(records)
    return


# Tests with `pipenv run python src/util_airtable.py`
if __name__ == '__main__':
    print('\n', 'airtable_setup', '\n', airtable_setup())
    test_name = 'Chris Okey'
    test_team = 'LAA'
    test_position = 'C'
    print('\n', 'airtable_get_player_id()', '\n', airtable_get_player_id(test_name, test_team, test_position))
    print('\n', 'airtable_check_and_create_player()', '\n', airtable_check_and_create_player(test_name, test_team, test_position))
    test_column = 'Watchlist'
    test_value = True
    print('\n', 'airtable_update_player_data()', '\n', airtable_update_player_data(test_name, test_team, test_position, test_column, test_value))
    test_value = False
    test_records = [{"id": airtable_get_player_id(test_name, test_team, test_position), 'fields': {'Player': test_name, 'Team': test_team, 'Position': test_position, test_column: test_value}}]
    print('\n', 'airtable_batch_update_player_data()', '\n', airtable_batch_update_player_data(test_records))
