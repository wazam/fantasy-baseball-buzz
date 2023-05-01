#Returns dictionary value of each item (used for sorting)
def by_value(item):
    return item[1]

# Returns new dictionary sorted from highest to lowest
def sort(dictionary_unsorted):
    dictionary_sorted = {}
    for k, v in sorted(dictionary_unsorted.items(), key = by_value, reverse = True):
        dictionary_sorted[k] = v
    return dictionary_sorted

# Returns dictionary sorted by values from lowest to highest
def sort_desc(dictionary_unsorted):
    dictionary_sorted = {}
    for k, v in sorted(dictionary_unsorted.items(), key = by_value):
        dictionary_sorted[k] = v
    return dictionary_sorted
