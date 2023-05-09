from os import environ
from time import sleep
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, NoSuchFrameException
from selenium.webdriver.support.ui import Select
from util_airtable import airtable_get_player_id, airtable_batch_update_player_data
from util_datetime import get_time_for_logs
from util_dictionary import dictionary_sort
from util_json import json_check_and_create_file, json_check_and_add_to_file # soon to remove
from util_webdriver import webdriver_setup_driver, webdriver_cleanup_driver

url_base = 'https://fantasy.espn.com/baseball'
league_id_url = environ.get('ESPN_LEAGUE_ID')
login_email = environ.get('ESPN_LOGIN_EMAIL')
login_pass = environ.get('ESPN_LOGIN_PASSWORD')
json_filename = 'mlb-players-espn'
trends_dictionary = {}

# Returns a numerically ordered dictionary of Players' names with their roster trends
def espn_get_added_dropped_trends():
    url_tab = '/addeddropped'
    url = url_base + url_tab
    trends_dictionary.clear()
    column_name = 'espn_get_added_dropped_trends'
    json_check_and_create_file(json_filename)  # Replace with separate espn_get_player_names()
    driver = webdriver_setup_driver()
    driver.get(url)
    sleep(4)
    # Count number of tables on the page
    num_total_tables = len(driver.find_elements(By.XPATH, "//*[@class='ResponsiveTable players-table']"))
    # Count number of rows on the page (across all tables)
    num_total_rows = len(driver.find_elements(By.XPATH, "//*[@class='Table']/tbody/tr"))
    # Calculate number of rows per each table
    num_rows = int(num_total_rows / num_total_tables)
    # Count number of available position pages
    num_total_positions = len(driver.find_elements(By.XPATH, "//*[@id='filterSlotIds']/label"))
    # Loop through all position pages to scrape table data of Players
    for p in range(2,num_total_positions+1):
        # Create a search for each position page listed
        xpath_position = "//*[@id='filterSlotIds']/label[" + str(p) + "]"
        # Find the current position page
        element_position = driver.find_element(By.XPATH, xpath_position)
        # Click the position page navigation labl to update the web page and Player tables
        element_position.click()
        sleep(1)
        # Loop through all the tables
        for each_table in range(0,num_total_tables):
            # Loop through all the rows of Players on the current table on the current position page
            for each_row in range(0,num_rows):
                # Create a search for each Player's name
                xpath_row_name = "(//*[@class='Table'])[" + str(int(each_table+1)) + "]/tbody/tr[" + str(int(each_row+1)) + "]/td[2]/div/div/div[2]/div/div[1]/span[1]/a"
                # Find the current Player's name
                row_name = str(driver.find_element(By.XPATH, xpath_row_name).text)
                # Add Player's name to file
                json_check_and_add_to_file(row_name, json_filename)
                # Create a search for each Player's 7 Day roster ownership trends
                xpath_row_number =  "(//*[@class='Table'])[" + str(int(each_table+1)) + "]/tbody/tr[" + str(int(each_row+1)) + "]/td[5]/div/span"
                # Find the current Player's 7 Day roster ownership trends
                row_number = float(driver.find_element(By.XPATH, xpath_row_number).text)
                # Check if Player is already in trends dictionary to avoid duplicating Player's adds/drops for Players eligible on multiple position pages for the current day
                if row_name not in trends_dictionary:
                    # Add Player to daily dictionary with net change in 7 Day roster ownership trends
                    trends_dictionary[row_name] = row_number
                    #
                    # 
                    # 
                    # airtable_update_player_data(airtable_check_player_name(row_name), row_number, column_name)
    webdriver_cleanup_driver(driver)
    sorted_dict = dictionary_sort(trends_dictionary)
    return sorted_dict


# Interacts with user login display box
def espn_login(driver):
    driver.find_element(By.XPATH, "//*[@id='InputLoginValue']").send_keys(login_email)
    driver.find_element(By.XPATH, "//*[@id='InputPassword']").send_keys(login_pass)
    driver.find_element(By.XPATH, "//*[@id='BtnSubmit']").click()
    sleep(7)
    return


# Returns all Players' names to Airtable
def espn_get_all_players():
    url_tab = '/players/add?view=trending&leagueId=' + league_id_url
    url = url_base + url_tab
    driver = webdriver_setup_driver()
    driver.get(url)
    sleep(3)
    try:
        log_in_button_html = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/div[5]/div[2]/div[2]/div/div/button")
    except NoSuchElementException:
        pass
    try:
        driver.switch_to.frame('oneid-iframe')
        log_in_button_iframe = driver.find_element(By.XPATH, "//*[@id='BtnSubmit']")
    except NoSuchFrameException:
        pass
    try:
        if log_in_button_iframe:
            espn_login(driver)
            driver.switch_to.default_content()
        elif log_in_button_html:
            log_in_button_html.click()
            espn_login(driver)
    except TypeError:
        pass
    filter_button = driver.find_element(By.XPATH, "//*[@id='filterStatus']")
    Select(filter_button).select_by_visible_text('All')
    sleep(3)

    positition_page_start_on = 1  # 1 for Batters, 2 for Pitchers
    positition_page_end_on = 3  # 2 for Batters, 3 for Pitchers

    for position_page in range(positition_page_start_on, positition_page_end_on):  # First 2 position pages include all players
        if position_page == 1:
            pass
        else:
            xpath_of_position_page_box = "//*[@id='filterSlotIds']/label[" + str(position_page) + "]"
            element_of_position_page_box = driver.find_element(By.XPATH, xpath_of_position_page_box)
            element_of_position_page_box.click()
            sleep(4)
        xpath_of_pagination_box = "/html/body/div[1]/div[1]/div/div/div[5]/div[2]/div[3]/div/div/div[3]/nav/div/ul/li"
        elements_in_pagination_box = driver.find_elements(By.XPATH, xpath_of_pagination_box)
        number_of_elements_in_pagination_box = len(elements_in_pagination_box)
        last_element_in_pagination_box = elements_in_pagination_box[number_of_elements_in_pagination_box - 1]
        number_of_pages_per_position = int(last_element_in_pagination_box.text)

        page_start_on = 1

        for page in range(1, page_start_on):
            driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/div[5]/div[2]/div[3]/div/div/div[3]/nav/button[2]").click()
            print('Loading page', page+1)
            sleep(1)

        for page in range(page_start_on-1, number_of_pages_per_position):
            xpath_of_table_row = "//*[@class='Table']/tbody/tr"
            number_of_table_rows_per_page = len(driver.find_elements(By.XPATH, xpath_of_table_row))

            for row in range(0, number_of_table_rows_per_page):
                xpath_of_player_row = xpath_of_table_row + "[" + str(int(row+1)) + "]/td[1]/div/div/div[2]/div/div["
                xpath_of_player_name = xpath_of_player_row + "1]/span[1]/a"
                xpath_of_player_team = xpath_of_player_row + "2]/span[1]"
                xpath_of_player_position = xpath_of_player_row + "2]/span[2]"
                xpath_of_player_injury_status = xpath_of_player_row + "1]/span[2]"
                xpath_of_player_rostered_team = xpath_of_table_row + "[" + str(int(row+1)) + "]/td[2]/div"
                xpath_of_player_ownership_percentage = xpath_of_table_row + "[" + str(int(row+1)) + "]/td[12]/div"
                xpath_of_player_ownership_change = xpath_of_table_row + "[" + str(int(row+1)) + "]/td[13]/div/span"

                player_name = driver.find_element(By.XPATH, xpath_of_player_name).text
                player_team = driver.find_element(By.XPATH, xpath_of_player_team).text
                player_position = driver.find_element(By.XPATH, xpath_of_player_position).text

                player_injury_status = ''
                try:
                    player_injury_status = driver.find_element(By.XPATH, xpath_of_player_injury_status).text
                except NoSuchElementException:
                    pass
                player_rostered_team = driver.find_element(By.XPATH, xpath_of_player_rostered_team).text
                player_ownership_percentage = float(driver.find_element(By.XPATH, xpath_of_player_ownership_percentage).text)
                player_ownership_change = float(driver.find_element(By.XPATH, xpath_of_player_ownership_change).text)

                list_of_player_record = []  # Possible limit of 10 ids, but page has 50 players
                list_of_player_fields = {}

                # # Need way to add new names
                # airtable_check_and_create_player(player_name)

                list_of_player_fields = {'Team': player_team, 'Position': player_position}

                list_of_player_fields['Injury'] = player_injury_status

                if player_rostered_team == 'BIGJ': # My team
                    on_someones_roster = True
                    on_my_roster = True
                elif player_rostered_team.startswith('WA ('):  # Waitlist
                    on_someones_roster = False
                    on_my_roster = False
                elif player_rostered_team != 'FA':  # Another team
                    on_someones_roster = True
                    on_my_roster = False
                else:
                    on_someones_roster = False
                    on_my_roster = False
                list_of_player_fields['Available'] = on_someones_roster
                list_of_player_fields['Rostered'] = on_my_roster

                list_of_player_fields['E %ROST'] = player_ownership_percentage
                list_of_player_fields['E +/-'] = player_ownership_change

                player_id = airtable_get_player_id(player_name, player_team, player_position)
                if player_id == False:
                    print('break on player not found', player_name, player_team, player_position)
                    return
                list_of_player_record.append({'id': str(player_id), 'fields': list_of_player_fields})
                print(get_time_for_logs(), '| Updated', player_name)
                airtable_batch_update_player_data(list_of_player_record)
            print(get_time_for_logs(), '| Finished page', page+1, 'out of', number_of_pages_per_position)
            next_page_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/div[5]/div[2]/div[3]/div/div/div[3]/nav/button[2]")
            next_page_button.click()
            sleep(3)
    webdriver_cleanup_driver(driver)
    return


# Tests with `pipenv run python src/provider_espn.py`
if __name__ == '__main__':
    # print('\n', 'espn_get_added_dropped_trends', '\n', espn_get_added_dropped_trends())
    print('\n', 'espn_get_all_players', '\n', espn_get_all_players())  # 3536 players x 2 secs/player = 2 hr runtime
