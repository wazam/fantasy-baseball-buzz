from os import environ
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager

import utils.my_beautifulsoup as MyBS
import utils.my_csv as MyC
import utils.my_dictionary as MyD
import utils.my_json as MyJ
import utils.my_unidecode as MyU


url_base = "https://www.mlb.com"


# Return data from search in current week's article
def get_player_names():

    url_tab = '/players'
    url = url_base + url_tab
    
    headless = int(environ.get('SELENIUM_HEADLESS', 1))
    firefox_options = FirefoxOptions()
    if headless == 1:
        firefox_options.add_argument("--headless")
    
    firefox_options.binary_location = r'/usr/bin/firefox'
    driver_binary = GeckoDriverManager().install()
    driver_service = FirefoxService(driver_binary)
    driver = webdriver.Firefox(service=driver_service, options=firefox_options)

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
            row_name = MyU.fix_str(row_name_raw)
            # MyJ.check_and_add(row_name, 'mlb-players')
            MyC.add_row('mlb-players', row_name)

    driver.close()
    driver.quit()

    return


# Used for testing with `pipenv run python src/provider_mlb.py`
if __name__ == '__main__':
    print('\n', 'get_player_names', '\n', get_player_names())
