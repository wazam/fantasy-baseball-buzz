from unidecode import unidecode


# Returns ASCII characters from unicode text data
def fix_str_format(unicode_string):
    ASCII_string = unidecode(unicode_string)
    return ASCII_string


# Used for testing with `pipenv run python src/util_unidecode.py`
if __name__ == '__main__':
    print('\n', 'fix_str_format()', '\n', fix_str_format("áéíñóú.z̯̯͡a̧͎̺l̡͓̫g̹̲o̡̼̘.Σίσυφος"))
