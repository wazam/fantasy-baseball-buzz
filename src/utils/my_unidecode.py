from unidecode import unidecode

# Returns ASCII characters from unicode text data
def fix_str(unicode_string):
    ASCII_string = unidecode(unicode_string)
    return ASCII_string

# Used for testing with `pipenv run python src/utils/my_unidecode.py`
if __name__ == "__main__":
    data = fix_str("Ronald (Jose) Acuña, Jr.")
    print(data)
