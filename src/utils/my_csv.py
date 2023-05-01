import os
import csv

filepath = './data'
ext = '.csv'

# Check for already existing file, if not found create a new file with headers row
def check_and_create(filename):
    if os.path.isfile(os.path.join(filepath, filename + ext)) and os.access(os.path.join(filepath, filename + ext), os.R_OK):
        # File exists
        pass
    else:
        if filename == 'mlb-players':
            header = ["full_name"]
        elif filename == 'new':  # New csv headers row template here
            header = ["column1", "column2"]
        with open(os.path.join(filepath, filename + ext), 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    return

# Add a row of data to the end of a file
def add_row(filename, data):
    check_and_create(filename)
    with open(os.path.join(filepath, filename + ext), 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([data])
    return

# Used for testing with `pipenv run python src/utils/my_csv.py`
if __name__ == "__main__":
    print('\n', 'check_and_create()', '\n', check_and_create('mlb-players'))
    print('\n', 'add_row()', '\n', add_row('mlb-players', "Qwerty Uiop"))
