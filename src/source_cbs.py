import os
import re
import json
from datetime import datetime
from dotenv import load_dotenv
from util_beautifulsoup import beautifulsoup_scrape, beautifulsoup_find
from util_nocodb import process_json_file
from config_source_keys import source_keys

load_dotenv()

running_in_docker = os.environ.get("RUNNING_IN_DOCKER", "true").lower() == "true"
base_data_folder = '/usr/src/data/' if running_in_docker else './data/buzz/'
data_folder = os.path.join(base_data_folder, 'results/')
os.makedirs(data_folder, exist_ok=True)

cbs_config = next(source for source in source_keys if source['source'].lower() == 'cbs')
trend_urls = {trend['key']: trend['url'] for trend in cbs_config['trends']}
cbs_trend_labels = {trend['key']: trend['labels'] for trend in cbs_config['trends']}
trend_columns = {key: list(range(1, len(labels) + 1)) for key, labels in cbs_trend_labels.items()}


def cbs_get(trend_type):
    """Returns a list of player trends by trend type and saves to a trend-specific JSON file."""

    if trend_type not in trend_urls:
        raise ValueError(f"Invalid trend_type '{trend_type}'. Choose from: {list(trend_urls.keys())}")

    url_trend = trend_urls[trend_type]
    columns = trend_columns[trend_type]  # Use pre-defined column indexes

    return cbs_finishup(url_trend, columns, trend_type)


def cbs_finishup(url_trend, columns, trend_type):
    """Processes CBS Sports trend tables and returns a list of player trends."""
    results_page = beautifulsoup_scrape(url_trend, '', 'div', 'Page-shell', False)
    elements_position_pages = beautifulsoup_find(results_page, 'all', 'a', 'Dropdown-link', True)

    trends_list = []

    json_filename = f"{data_folder}{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_cbs-{trend_type}.json"
    total_position_pages = len(elements_position_pages)  # Total number of position pages
    print(f"Total position pages to process: {total_position_pages}")

    for page_index, position_page in enumerate(elements_position_pages, start=1):
        url_part = str(position_page['href'])
        url_full = 'https://www.cbssports.com' + url_part
        results_table = beautifulsoup_scrape(url_full, '', 'div', 'TableBaseWrapper', False)

        if results_table is None:
            print(f"Skipping page {page_index}/{total_position_pages}: Unable to retrieve results table.")
            continue

        elements_rows = beautifulsoup_find(results_table, 'all', 'tr', 'TableBase-bodyTr', False)
        elements_players_info = beautifulsoup_find(results_table, 'all', 'span', 'CellPlayerName--long', False)
        elements_players_trends = beautifulsoup_find(results_table, 'all', 'td', 'TableBase-bodyTd', False)

        if elements_rows is None or elements_players_info is None or elements_players_trends is None:
            print(f"Skipping page {page_index}/{total_position_pages}: No data found.")
            continue

        print(f"Processing position page {page_index}/{total_position_pages} for trend type '{trend_type}'...")

        step_size = len(columns) + 1  # Step size matches the structure of the table

        # Collect all player entries with refined row logic
        for index in range(0, len(elements_rows)):
            player_name_tag = elements_players_info[index].find('a')
            if not player_name_tag:
                continue

            player_name = str(player_name_tag.text.split('\n')[0])

            player_href = player_name_tag['href']
            player_id_match = re.search(r'/mlb/players/(\d+)', player_href)
            player_id = player_id_match.group(1) if player_id_match else None

            player_pos = str(elements_players_info[index].text.split('\n')[1].strip())
            player_team = str(elements_players_info[index].text.split('\n')[3].strip())

            player_entry = {
                "Player": player_name,
                "Position": player_pos,
                "Team": player_team,
                "Id_CBS": player_id
            }

            labels = cbs_trend_labels[trend_type]
            for col_idx, column in enumerate(columns):
                trend_value = elements_players_trends[(column - 1) + index * step_size].text.strip()
                if trend_value in ['—', '--']:
                    trend_value = 0
                player_entry[labels[col_idx]] = trend_value

            trends_list.append(player_entry)

    # Removing duplicate players — keep the latest valid entry for each
    filtered_trends_dict = {}
    for entry in reversed(trends_list):  # Reverse to prioritize the latest entry
        filtered_trends_dict[entry['Player']] = entry  # Keyed by 'Player' to ensure uniqueness

    # Convert back to list format for JSON output
    trends_list = list(filtered_trends_dict.values())

    # Save to JSON before returning
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(trends_list, json_file, indent=4)

    print(f"Processing complete. Saved results to {json_filename}")
    process_json_file(json_filename)
    return trends_list


# Tests with `pipenv run python src/source_cbs.py`
if __name__ == '__main__':
    print('\n', 'cbs_get(added)', '\n', cbs_get('added'))
    #print('\n', 'cbs_get(dropped)', '\n', cbs_get('dropped'))
    #print('\n', 'cbs_get(viewed)', '\n', cbs_get('viewed'))
    #print('\n', 'cbs_get(traded)', '\n', cbs_get('traded'))
    #print('\n', 'cbs_get(draft)', '\n', cbs_get('draft'))
    #print('\n', 'cbs_get(rankings)', '\n', cbs_get('rankings'))
