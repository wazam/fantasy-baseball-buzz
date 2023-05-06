import os
from util_json import json_get_from_file
from util_csv import csv_get_from_file_as_list

prefixed = [filename for filename in os.listdir('./data') if filename.startswith("mlb-players")]
return_player_names = []


# Returns combined list of Players' full names from multiple source files
def combine_get_names():
    return_player_names.clear()
    for file in prefixed:
        filename = file.split('.', 1)[0]
        if file.endswith('.json'):
            player_name_data = json_get_from_file(filename)['players']
            for _, player in enumerate(player_name_data):
                name = player['full_name']
                if name == '' or name == 'full_name' or name == 'undefined undefined':
                    pass
                else:
                    if len(return_player_names) == 0:
                        return_player_names.append({"full_name": name})
                    else:
                        name_check_jr = name + ' Jr.'  # Ronald Acuna Jr., Vladimir Guerrero Jr.
                        name_check_sr = name + ' Sr.'  # Travis Lakins Sr.
                        name_check_second = name + ' II'  # Michael Harris II, Cedric Mullins II
                        name_check_case = name.lower()  # Ha-seong Kim
                        name_check_hypen = name.replace('-', ' ')  # Ji-Hwan Bae, Ji-Man Choi, Hyun-Jin Ryu
                        name_check_period = name.replace('.', '')  # A.J. Pollock, D.J. Stewart
                        # Broken: Luis F. Ortiz and Luis L. Ortiz vs Luis Ortiz (1) and (2) ... -> use column_team
                        # Broken: Jean-Carlos Mejia vs J.C. Mejia
                        # Broken: tracking for other (2) and (3) named players ... -> use column_team
                        for index, _ in enumerate(return_player_names):
                            if name == return_player_names[index]['full_name'] or \
                                    name_check_jr == return_player_names[index]['full_name'] or \
                                    name_check_sr == return_player_names[index]['full_name'] or \
                                    name_check_second == return_player_names[index]['full_name'] or \
                                    name_check_case == return_player_names[index]['full_name'].lower() or \
                                    name_check_hypen == return_player_names[index]['full_name'] or \
                                    name_check_period == return_player_names[index]['full_name']:
                                # Player already present
                                break
                            elif index == len(return_player_names)-1:
                                return_player_names.append({"full_name": name})
                                break
        elif file.endswith('.csv'):
            player_name_data = csv_get_from_file_as_list(filename)
            for _, player in enumerate(player_name_data):
                name = player
                if name == [''] or name == ['full_name'] or name == ['undefined undefined']:
                    pass
                else:
                    if len(return_player_names) == 0:
                        return_player_names.append({"full_name": name[0]})
                    else:
                        name_check_jr = name[0] + ' Jr.'
                        name_check_sr = name[0] + ' Sr.'
                        name_check_second = name[0] + ' II'
                        name_check_case = name[0].lower()
                        name_check_hypen = name[0].replace('-', ' ')
                        name_check_period = name[0].replace('.', '')
                        for index, _ in enumerate(return_player_names):
                            if name[0] == return_player_names[index]['full_name'] or \
                                    name_check_jr == return_player_names[index]['full_name'] or \
                                    name_check_sr == return_player_names[index]['full_name'] or \
                                    name_check_second == return_player_names[index]['full_name'] or \
                                    name_check_case == return_player_names[index]['full_name'].lower() or \
                                    name_check_hypen == return_player_names[index]['full_name'] or \
                                    name_check_period == return_player_names[index]['full_name']:
                                # Player already present
                                break
                            elif index == len(return_player_names)-1:
                                return_player_names.append({"full_name": name[0]})
                                break
    return return_player_names


# Returns dictionary of Player's trends from a provider
def combine_get_trend(player_trend_data):
    return_player_trend = {}
    for player in player_trend_data:
        full_name = player
        trend = player_trend_data[full_name]
        if full_name not in return_player_trend:
            add_to_dict = [{"trend": trend}]
            return_player_trend[full_name] = add_to_dict
    return return_player_trend


# Tests with `pipenv run python src/util_combine.py`
if __name__ == '__main__':
    print('\n', 'combine_get_names', '\n', combine_get_names())
    # from provider_cbs import cbs_get_added_dropped_trends
    # print('\n', 'combine_get_trend()', '\n', combine_get_trend(cbs_get_added_dropped_trends()))
