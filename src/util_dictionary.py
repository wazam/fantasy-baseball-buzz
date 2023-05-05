sorted_dict = {}


# Returns dictionary value of each item (used for sorting)
def key_by_value(item):
    return item[1]


# Returns new dictionary sorted from highest to lowest
def dictionary_sort(dict):
    sorted_dict.clear()
    for k, v in sorted(dict.items(), key=key_by_value, reverse=True):
        sorted_dict[k] = v
    return sorted_dict


# Returns dictionary sorted by values from lowest to highest
def dictionary_sort_desc(dict):
    sorted_dict.clear()
    for k, v in sorted(dict.items(), key=key_by_value):
        sorted_dict[k] = v
    return sorted_dict


# Tests with `pipenv run python src/util_dictionary.py`
if __name__ == '__main__':
    print('\n', 'dictionary_sort()', '\n', dictionary_sort({'a': 1, 'b': 2}))
    print('\n', 'dictionary_sort_desc()', '\n', dictionary_sort_desc({'a': 9, 'b': 8}))
