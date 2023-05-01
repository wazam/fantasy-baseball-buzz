from os import environ
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
# from webdriver_manager.core.utils import read_version_from_cmd, PATTERN  # (used during testing)

import utils.my_json as MyJ


url_base = "http://fantasy.espn.com/baseball"


# Returns a numerically ordered dictionary of Players' names with their roster trends
def get_added_dropped_trends():
    url_tab = "/addeddropped"
    url = url_base + url_tab

    headless = int(environ.get('SELENIUM_HEADLESS', 1))
    firefox_options = FirefoxOptions()
    if headless == 1:
        firefox_options.add_argument("--headless")  # .add_argument("--no-sandbox")
    
    # # Returns current version of browser (used during testing)
    # version = read_version_from_cmd("/usr/bin/firefox --version", PATTERN["firefox"])
    # print(version)
    # breakpoint()
    
    firefox_options.binary_location = r'/usr/bin/firefox'
    driver_binary = GeckoDriverManager().install()  # .install(version=version)
    
    driver_service = FirefoxService(driver_binary)
    driver = webdriver.Firefox(service=driver_service, options=firefox_options)

    # # Returns current user-agent from browser (used during testing)
    # user_agent = driver.execute_script("return navigator.userAgent;")
    # headers = {'User-Agent': user_agent}
    # print(headers)
    # breakpoint()
    # return headers

    # Send the URL to the web browser
    driver.get(url)
    # Wait for the web page to load all it's content
    sleep(4)
    # Count number of tables on the page
    num_total_tables = len(driver.find_elements(By.XPATH, "//*[@class='ResponsiveTable players-table']"))
    # Count number of rows on the page (across all tables)
    num_total_rows = len(driver.find_elements(By.XPATH, "//*[@class='Table']/tbody/tr"))
    # Calculate number of rows per each table
    num_rows = int(num_total_rows / num_total_tables)
    # Count number of available position pages
    num_total_positions = len(driver.find_elements(By.XPATH, "//*[@id='filterSlotIds']/label"))
    # Create new dictionary to save all the Players' net change in roster ownership
    trends_dictionary = {}
    # Loop through all position pages to scrape table data of Players
    for p in range(2,num_total_positions+1):
        # Create a search for each position page listed
        xpath_position = "//*[@id='filterSlotIds']/label[" + str(p) + "]"
        # Find the current position page
        element_position = driver.find_element(By.XPATH, xpath_position)
        # Click the position page navigation labl to update the web page and Player tables
        element_position.click()
        # Wait for the web page to load all it's content
        sleep(1)
        # Loop through all the tables
        for each_table in range(0,num_total_tables):
            # Loop through all the rows of Players on the current table on the current position page
            for each_row in range(0,num_rows):
                # Create a search for each Player's name
                xpath_row_name = "(//*[@class='Table'])[" + str(int(each_table+1)) + "]/tbody/tr[" + str(int(each_row+1)) + "]/td[2]/div/div/div[2]/div/div[1]/span[1]/a"
                # Find the current Player's name
                row_name = str(driver.find_element(By.XPATH, xpath_row_name).text)
                # Add Player's name to combined json
                MyJ.check_and_add(row_name, 'player-names')
                # Create a search for each Player's 7 Day roster ownership trends
                xpath_row_number =  "(//*[@class='Table'])[" + str(int(each_table+1)) + "]/tbody/tr[" + str(int(each_row+1)) + "]/td[5]/div/span"
                # Find the current Player's 7 Day roster ownership trends
                row_number = float(driver.find_element(By.XPATH, xpath_row_number).text)
                # Check if Player is already in trends dictionary to avoid duplicating Player's adds/drops for Players eligible on multiple position pages for the current day
                if row_name not in trends_dictionary:
                    # Add Player to daily dictionary with net change in 7 Day roster ownership trends
                    trends_dictionary[row_name] = row_number
    # Close the web page
    driver.close()
    # Quit the web browser
    driver.quit()
    # Create new dictionary to sort the Players' by their net change across the requested day(s)
    sorted_trends_dictionary = {}
    # Create a function to decide the custom sorting order
    def by_value(item):
        # Return the Player's net change
        return item[1]
    # Loop through all the Players' net change values in the weekly trends dictionary for custom sorting in descending order
    for key, value in sorted(trends_dictionary.items(), key=by_value, reverse=True):
        # Add Player to sorted weekly trends dictionary with their net change
        sorted_trends_dictionary[key] = value
    #Return sorted dictionary for the function
    return sorted_trends_dictionary


# Used for testing with `pipenv run python src/provider_espn.py`
if __name__ == "__main__":
    print('\n', 'get_added_dropped_trends', '\n', get_added_dropped_trends())
