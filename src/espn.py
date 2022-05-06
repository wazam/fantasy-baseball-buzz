#Used to load web pages
from selenium import webdriver
#Used to scrape web pages
from selenium.webdriver.common.by import By
#Used to wait for web page to load/update
from time import sleep

#Function to return a numerically ordered dictionary of players' names and players' trends
def espn_trends():

    #Chrome web driver in PATH, C:\Program Files (custom)\chromedriver_win32
    driver = webdriver.Chrome()
    #Load web page and wait for it to finish
    url = "http://fantasy.espn.com/baseball/addeddropped"
    driver.get(url)
    sleep(3)

    #Count number of tables on the page
    xpath_total_tables = "//*[@class='ResponsiveTable players-table']"
    elements_total_tables = driver.find_elements(By.XPATH, xpath_total_tables)
    num_total_tables = len(elements_total_tables)
    #Count number of rows on the page (across all tables)
    xpath_total_rows = "//*[@class='Table']/tbody/tr"
    elements_total_rows = driver.find_elements(By.XPATH, xpath_total_rows)
    num_total_rows = len(elements_total_rows)
    #Calculate number of rows per each table
    num_rows = int (num_total_rows / num_total_tables)
    #Count number of available position pages
    xpath_total_positions = "//*[@id='filterSlotIds']/label"
    elements_total_positions = driver.find_elements(By.XPATH, xpath_total_positions)
    num_total_positions = len(elements_total_positions)

    #Create dictionary for storing Player's names and 7 Day +/-
    trends_dictionary = {}
    #Loop through all position pages
    for p in range(2,num_total_positions+1):
        #Find Position pages
        xpath_position = "//*[@id='filterSlotIds']/label[" + str(p) + "]"
        element_position = driver.find_element(By.XPATH, xpath_position)
        #Click new position to update web page
        element_position.click()
        sleep(1)
        #Loop through all tables
        for t in range(0,num_total_tables):
            #Loop through all rows
            for r in range(0,num_rows):
                #Find Player's name
                xpath_row_name = "(//*[@class='Table'])[" + str(int(t+1)) + "]/tbody/tr[" + str(int(r+1)) + "]/td[2]/div/div/div[2]/div/div[1]/span[1]/a"
                element_row_name = driver.find_element(By.XPATH, xpath_row_name)
                row_name = str(element_row_name.text)
                #Find Player's 7 Day +/-
                xpath_row_number =  "(//*[@class='Table'])[" + str(int(t+1)) + "]/tbody/tr[" + str(int(r+1)) + "]/td[5]/div/span"
                element_row_number = driver.find_element(By.XPATH, xpath_row_number)
                row_number = float(element_row_number.text)
                #Add Player's name and 7 Day +/- to trends dictionary, unless already present
                if row_name not in trends_dictionary:
                    trends_dictionary[row_name] = row_number
    #Close web page
    driver.quit()

    #Sort player ditionary
    sorted_trends_dictionary = {}
    def by_value(item):
        return item[1]
    for k, v in sorted(trends_dictionary.items(), key=by_value, reverse=True):
        sorted_trends_dictionary[k] = v

    #Return sorted dictionary for function
    return sorted_trends_dictionary

#Used for "pipenv run python src/espn.py"
if __name__ == "__main__":
    data = espn_trends()
    #Print Player trends
    print('\x1b[6;30;42m' + "Past 7 day(s) of ESPN trends" + '\x1b[0m')
    print(data)
