#Returns dictionary value of each item (used for sorting)
def by_value(item):
    return item[1]

# Returns new dictionary sorted from highest to lowest (true)
def sort(dict, high_to_low):
    dict_sort = {}
    for k, v in sorted(dict.items(), key= by_value, reverse= high_to_low):
        dict_sort[k] = v
    return dict_sort
