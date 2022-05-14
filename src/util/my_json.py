import os
import json


# return values from JSON (create blank with template if does not exist)
def get_json(filename):
    if os.path.isfile(os.path.join('./data/', filename + '.json')) and os.access(os.path.join('./data/', filename + '.json'), os.R_OK):
        pass
    else:
        with open(os.path.join('./data/', filename + '.json'), 'w') as new_file:
            new_file.write(json.dumps({"players":[{"short_name": "", "full_name": ""}]}, indent= 4))
    data = json.load(open(os.path.join('./data/', filename + '.json')))
    return data


# add to a JSON file
def write_json(new_data, filename):
    with open(os.path.join('./data/', filename + '.json'),'r+') as file:
        file_data = json.load(file)
        file_data["players"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent= 4)
    return


# ```python src/util/my_json.py```
if __name__ == "__main__":
    filename = 'yahoo-players'
    new_data = {"short_name": "", "full_name": ""}
    write_json(new_data, filename)
    print(get_json(filename))
