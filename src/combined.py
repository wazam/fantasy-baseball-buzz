import utils.my_json as MyJ


# Return list of Player's full names
def get_names():
    return_player_names = []
    player_name_data = MyJ.get_json('player-names')['players']

    for _, player in enumerate(player_name_data):
        full_name = player['full_name']
        add_to_list = {"full_name": full_name}
        return_player_names.append(add_to_list)
    
    # print(return_player_names)
    # breakpoint()
    return return_player_names


# Return dictionary of Player's trends from a provider
def get_trend(player_trend_data):    
    return_player_trend = {}
    for player in player_trend_data:
        full_name = player
        trend = player_trend_data[full_name]
        if full_name not in return_player_trend:
            add_to_dict = [{"trend": trend}]
            return_player_trend[full_name] = add_to_dict
    
    # print(return_player_trend)
    # breakpoint()
    return return_player_trend


# Unused (attempted to get/return multiple trends at once for combined web view)
def get_trends(player_trends_data_list):
    return_player_trends = []
    for index, trend in enumerate(player_trends_data_list):
        add_to_list = {index: get_trend(trend)}
        return_player_trends.append(add_to_list)

    # print(return_player_trends)
    # breakpoint()
    return return_player_trends


# Used for testing with `pipenv run python src/combined.py`
if __name__ == "__main__":
    import provider_cbs as cbs
    print('\n', 'get_names', '\n', get_names())
    print('\n', 'get_trend()', '\n', get_trend(cbs.get_added_dropped_trends()))
    # trend_columns = [cbs.get_viewed_trends(), cbs.get_traded_trends()]
    # print('\n', 'get_trends([])', '\n', get_trends(trend_columns))
