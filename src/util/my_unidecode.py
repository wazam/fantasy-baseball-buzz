import unidecode


# Returns ASCII characters from unicode text data
def fix_str(unicode_string):
    ASCII_string = unidecode.unidecode(unicode_string)
    return ASCII_string
