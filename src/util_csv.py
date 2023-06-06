import os
import csv

filepath = './data'
ext = '.csv'


# Creates a new file with headers row
def csv_create_file(filename):
    if filename.startswith('mlb-players'):
        header = ["full_name"]
    elif filename == 'new':  # New csv headers row template here
        header = ["column1", "column2"]
    with open(os.path.join(filepath, filename + ext), mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
    return


# Checks for an existing file before (re)creating it
def csv_check_and_create_file(filename):
    if (os.path.isfile(os.path.join(filepath, filename + ext)) and
            os.access(os.path.join(filepath, filename + ext), os.R_OK)):
        # File exists and is accessible
        pass
    else:
        csv_create_file(filename)
    return


# Adds a row of data to the end of a file
def csv_add_to_file(data, filename):
    with open(os.path.join(filepath, filename + ext), mode='a') as f:
        writer = csv.writer(f)
        writer.writerow([data])
    return


# Checks for an existing Player's name before (re)adding it
def csv_check_and_add_to_file(data, filename):
    data_import = data
    csv_data = csv_get_from_file(filename)
    for player_index in range(2, 9):
        if data not in csv_data:
            # Player is new and does not exist
            break
        else:
            # Player exists and needs to be incremented starting with (2)
            data = data_import + ' (' + str(player_index) + ')'
    csv_add_to_file(data, filename)
    return


# Returns values from file
def csv_get_from_file(filename):
    with open(os.path.join(filepath, filename + ext), mode='r') as f:
        return f.read()


# Returns values from file as list
def csv_get_from_file_as_list(filename):
    with open(os.path.join(filepath, filename + ext), mode='r') as f:
        return list(csv.reader(f, delimiter='\n'))


# Deletes a file
def csv_delete_file(filename):
    os.remove(os.path.join(filepath, filename + ext))
    return


# Tests with `pipenv run python src/util_csv.py`
if __name__ == '__main__':
    filename = 'mlb-players-test'
    data = "Qwerty Qwerty"
    print('\n', 'csv_create_file()', '\n', csv_create_file(filename))
    print('\n', 'csv_check_and_create_file()', '\n', csv_check_and_create_file(filename))
    print('\n', 'csv_add_to_file()', '\n', csv_add_to_file(data, filename))
    print('\n', 'csv_check_and_add_to_file()', '\n', csv_check_and_add_to_file(data, filename))
    print('\n', 'csv_get_from_file()', '\n', csv_get_from_file(filename))
    print('\n', 'csv_get_from_file_as_list()', '\n', csv_get_from_file_as_list(filename))
    print('\n', 'csv_delete_file()', '\n', csv_delete_file(filename))
