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
            new_json_file.write(json.dumps({"players":[{"short_name": "", "full_name": ""}]}, indent = 4))
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


# ```python src/util/my_json.py```
if __name__ == "__main__":
    filename = 'yahoo-players'
    # new_data = {"short_name": "A. Test", "full_name": "Always Test"}
    # write_json(new_data, filename)
    data = get_json(filename)
    #breakpoint()
    print(data)
