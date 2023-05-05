import os
from util_json import json_get_from_file
from util_csv import csv_get_from_file_as_list

prefixed = [filename for filename in os.listdir('./data') if filename.startswith("mlb-players")]
return_player_names = []


# Returns combined list of Players' full names from multiple source files
def combined_get_names():
    return_player_names.clear()
    for file in prefixed:
        filename = file.split('.', 1)[0]
        if file.endswith('.json'):
            player_name_data = json_get_from_file(filename)['players']
            for _, player in enumerate(player_name_data):
                name = player['full_name']
                if name == '' or name == 'full_name':
                    pass
                else:
                    if len(return_player_names) == 0:
                        return_player_names.append({"full_name": name})
                    else:
                        name_check_jr = name + ' Jr.'
                        name_check_second = name + ' II'
                        name_check_lower_case = name.lower()
                        for index, _ in enumerate(return_player_names):
                            if name == return_player_names[index]['full_name']:
                                # Player already present
                                break
                            elif name_check_jr == return_player_names[index]['full_name']:
                                # Player already present
                                break
                            elif name_check_second == return_player_names[index]['full_name']:
                                # Player already present
                                break
                            elif name_check_lower_case == return_player_names[index]['full_name'].lower():
                                # Player already present
                                break
                            elif index == len(return_player_names)-1:
                                return_player_names.append({"full_name": name})
                                break
        elif file.endswith('.csv'):
            player_name_data = csv_get_from_file_as_list(filename)
            for _, player in enumerate(player_name_data):
                name = player
                if name == [''] or name == ['full_name']:
                    pass
                else:
                    if len(return_player_names) == 0:
                        return_player_names.append({"full_name": name[0]})
                    else:
                        name_check_jr = name[0] + ' Jr.'
                        name_check_second = name[0] + ' II'
                        name_check_lower_case = name[0].lower()
                        for index, _ in enumerate(return_player_names):
                            # breakpoint()
                            if name[0] == return_player_names[index]['full_name']:
                                # Player already present
                                break
                            elif name_check_jr == return_player_names[index]['full_name']:
                                # Player already present
                                break
                            elif name_check_second == return_player_names[index]['full_name']:
                                # Player already present
                                break
                            elif name_check_lower_case == return_player_names[index]['full_name'].lower():
                                # Player already present
                                break
                            elif index == len(return_player_names)-1:
                                return_player_names.append({"full_name": name[0]})
                                break
    return return_player_names


# Returns dictionary of Player's trends from a provider
def combined_get_trend(player_trend_data):
    return_player_trend = {}
    for player in player_trend_data:
        full_name = player
        trend = player_trend_data[full_name]
        if full_name not in return_player_trend:
            add_to_dict = [{"trend": trend}]
            return_player_trend[full_name] = add_to_dict
    return return_player_trend


# Tests with `pipenv run python src/combined.py`
if __name__ == '__main__':
    print('\n', 'combined_get_names', '\n', len(combined_get_names()))
    # from provider_cbs import cbs_get_added_dropped_trends
    # print('\n', 'combined_get_trend()', '\n', combined_get_trend(cbs_get_added_dropped_trends()))
