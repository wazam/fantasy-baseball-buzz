from time import sleep
from selenium.webdriver.common.by import By
from util_dictionary import dictionary_sort
from util_json import json_check_and_add_to_file
from util_webdriver import webdriver_setup_driver, webdriver_cleanup_driver

url_base = 'https://fantasy.espn.com/baseball'
trends_dictionary = {}


# Returns a numerically ordered dictionary of Players' names with their roster trends
def espn_get_added_dropped_trends():
    url_tab = '/addeddropped'
    url = url_base + url_tab
    driver = webdriver_setup_driver()
    trends_dictionary.clear()
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
                json_check_and_add_to_file(row_name, 'mlb-players-espn')
                # Create a search for each Player's 7 Day roster ownership trends
                xpath_row_number =  "(//*[@class='Table'])[" + str(int(each_table+1)) + "]/tbody/tr[" + str(int(each_row+1)) + "]/td[5]/div/span"
                # Find the current Player's 7 Day roster ownership trends
                row_number = float(driver.find_element(By.XPATH, xpath_row_number).text)
                # Check if Player is already in trends dictionary to avoid duplicating Player's adds/drops for Players eligible on multiple position pages for the current day
                if row_name not in trends_dictionary:
                    # Add Player to daily dictionary with net change in 7 Day roster ownership trends
                    trends_dictionary[row_name] = row_number
    webdriver_cleanup_driver(driver)
    sorted_dict = dictionary_sort(trends_dictionary)
    return sorted_dict


# Used for testing with `pipenv run python src/provider_espn.py`
if __name__ == '__main__':
    print('\n', 'espn_get_added_dropped_trends', '\n', espn_get_added_dropped_trends())
