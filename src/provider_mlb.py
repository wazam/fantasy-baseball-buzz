from selenium.webdriver.common.by import By
from util_csv import csv_create_file, csv_check_and_add_to_file
from util_unidecode import fix_str_format
from util_webdriver import webdriver_setup_driver, webdriver_cleanup_driver

url_base = 'https://www.mlb.com'
csv_filename = 'mlb-players-mlb'


# Creates CSV file with list of Players' names
def mlb_get_player_list():
    # Setup URL in webdriver
    url_tab = '/players'
    url = url_base + url_tab
    csv_create_file(csv_filename)
    driver = webdriver_setup_driver()
    driver.get(url)
    xpath_num_sections = "//*[@id='players-index']/div/div"
    num_sections = len(driver.find_elements(By.XPATH, xpath_num_sections))
    # Loop through all the sections, skipping every other section (which is a heading)
    for each_section in range(0, num_sections, 2):
        xpath_num_rows = "//*[@id='players-index']/div/div[" + str(int(each_section+2)) + "]/ul/li"
        num_rows = len(driver.find_elements(By.XPATH, xpath_num_rows))
        # Loop through all names in a section
        for each_row in range(0, num_rows):
            xpath_row_name = "//*[@id='players-index']/div/div[" + str(int(each_section+2)) + "]/ul/li[" + str(int(each_row+1)) + "]/a"
            row_name_raw = str(driver.find_element(By.XPATH, xpath_row_name).text)
            player_name = fix_str_format(row_name_raw)
            csv_check_and_add_to_file(player_name, csv_filename)
    webdriver_cleanup_driver(driver)
    return

# Tests with `pipenv run python src/provider_mlb.py`
if __name__ == '__main__':
    print('\n', 'mlb_get_player_list', '\n', mlb_get_player_list())
