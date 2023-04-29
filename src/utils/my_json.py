import os
import json


filepath = './data'
ext = '.json'


# return values from JSON (create blank from template if not already present)
def get_json(filename):
    if os.path.isfile(os.path.join(filepath, filename + ext)) and os.access(os.path.join(filepath, filename + ext), os.R_OK):
        pass
    else:
        with open(os.path.join(filepath, filename + ext), 'w') as new_json_file:
            if filename == 'yahoo-players':
                new_json_file.write(json.dumps({"players":[{"short_name": "", "full_name": ""}]}, indent = 4))
            elif filename == 'player-names':
                new_json_file.write(json.dumps({"players":[{"full_name": ""}]}, indent = 4))
    data = json.load(open(os.path.join(filepath, filename + ext)))
    return data


# add to a JSON file
def write_json(new_data, filename):
    with open(os.path.join(filepath, filename + ext), 'r+') as json_file:
        file_data = json.load(json_file)
        file_data["players"].append(new_data)
        json_file.seek(0)
        json.dump(file_data, json_file, indent = 4)
    return


# add Player's full name to combined file from all sources
def add_name_to(player_name_full, filename):
    players_json = get_json(filename)
    for key, _ in enumerate(players_json['players']):
        if player_name_full == players_json['players'][key]['full_name']:
            # Player already present
            break
        elif key == len(players_json['players']) - 1:
            new_player = {"full_name": player_name_full}
            write_json(new_player, 'player-names')
            break
    return


# Used for testing with `pipenv run python src/utils/my_json.py` or `pipenv run python -m src.utils.my_json`
if __name__ == "__main__":
    # filename = 'player-names'
    filename = 'yahoo-players'
    # new_data = {"short_name": "A. Test", "full_name": "Always Test"}
    # write_json(new_data, filename)
    data = get_json(filename)
    # breakpoint()
    print(data)