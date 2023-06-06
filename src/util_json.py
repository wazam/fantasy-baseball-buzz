import os
import json

filepath = './data'
ext = '.json'
dict_list = 'players'
dict_key = "full_name"


# Creates a new file with headers row
def json_create_file(filename):
    if filename == 'lookup-first-name-abbreviation':
        headers = {dict_list: [{"short_name": "", dict_key: ""}]}
    elif filename.startswith('mlb-players'):
        headers = {dict_list: [{dict_key: ""}]}
    with open(os.path.join(filepath, filename + ext), mode='w') as f:
        f.write(json.dumps(headers, indent=4))
    return


# Checks for an existing file before (re)creating it
def json_check_and_create_file(filename):
    if (os.path.isfile(os.path.join(filepath, filename + ext)) and
            os.access(os.path.join(filepath, filename + ext), os.R_OK)):
        # File exists and is accessible
        pass
    else:
        json_create_file(filename)
    return


# Adds a dictionary of data to the end of a file
def json_add_to_file(data, filename):
    with open(os.path.join(filepath, filename + ext), 'r+') as json_file:
        file_data = json.load(json_file)
        file_data[dict_list].append(data)
        json_file.seek(0)
        json.dump(file_data, json_file, indent=4)
    return


# Checks for an existing Player's name before adding it
def json_check_and_add_to_file(data, filename):
    players_json = json_get_from_file(filename)
    try:
        name = data[dict_key]
    except TypeError:
        name = data
    for index, _ in enumerate((players_json)[dict_list]):
        if name in players_json[dict_list][index][dict_key]:
            # Player already present
            break
        else:
            new_player_data = {dict_key: name}
            json_add_to_file(new_player_data, filename)
            break
    return


# Returns values from file
def json_get_from_file(filename):
    with open(os.path.join(filepath, filename + ext), 'r') as f:
        return json.load(f)


# Deletes a file
def json_delete_file(filename):
    os.remove(os.path.join(filepath, filename + ext))
    return


# Tests with `pipenv run python src/util_json.py`
if __name__ == '__main__':
    filename = 'mlb-players-test'
    dict_key = "full_name"
    dict_val = "Qwerty Qwerty"
    data = {dict_key: dict_val}
    print('\n', 'json_create_file()', '\n', json_create_file(filename))
    print('\n', 'json_check_and_create_file()', '\n', json_check_and_create_file(filename))
    print('\n', 'json_add_to_file()', '\n', json_add_to_file(data, filename))
    print('\n', 'json_check_and_add_to_file()', '\n', json_check_and_add_to_file(data, filename))
    print('\n', 'json_get_from_file()', '\n', json_get_from_file(filename))
    print('\n', 'json_delete_file()', '\n', json_delete_file(filename))

