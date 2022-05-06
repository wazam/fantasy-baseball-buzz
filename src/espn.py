# Used to return an instance of a web browser
from selenium import webdriver
# Used to send launch paramaters to Chrome web browser on the local machine
from selenium.webdriver.chrome.options import Options as ChromeOptions
# Used to send launch paramaters to Firefox web browser on the local machine
from selenium.webdriver.firefox.options import Options as FirefoxOptions
# Used to send launch paramaters to Edge web browser on the local machine
from selenium.webdriver.edge.options import Options as EdgeOptions
# Used to scrape web pages in the browser for content
from selenium.webdriver.common.by import By
# Used to wait for the web pages to load/update
from time import sleep
# Used to set environment varaibles on the system
from dotenv import load_dotenv, find_dotenv
# Used to get environment varaibles from the system 
from os import environ

# Returns a numerically ordered dictionary of Players' names with their roster trends
def espn_trends():
    # Site-specific url
    url = "http://fantasy.espn.com/baseball/addeddropped"
    # Set environment variables from local .env
    load_dotenv(find_dotenv())
    # Set browser from environment variable used for scraping
    browser = environ.get('BROWSER', "CHROME")
    # Set enabled headless mode environment variable for web browser
    enable_headless = eval(environ.get('ENABLE_HEADLESS', True))
    # Check if Chrome web-driver support is enabled
    if browser == "CHROME":
        # Set options class to configure Chrome
        options = ChromeOptions()
        # Check for observing the web-driver's actions in the web browser
        if enable_headless == False:
            # Set web browser option to run with user-interface
            options.headless = False # or pass
        else:
            # Set web browser option to run without user-interface
            options.headless = True
        # Ignore error messages `Failed to read descriptor from node connection: A device attached to the system is not functioning` from CLI
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # Launch web browser with options
        driver = webdriver.Chrome(options=options)
    # Check if Firefox web-driver support is enabled
    elif browser == "FIREFOX":
        # Set options class to configure Firefox
        options = FirefoxOptions()
        # Check for observing the web-driver's actions in the web browser
        if enable_headless == False:
            # Set web browser option to run with user-interface
            options.headless = False # or pass
        else:
            # Set web browser option to run without user-interface
            options.headless = True
        # Launch web browser with options
        driver = webdriver.Firefox(options=options)
    # Check if Edge web-driver support is enabled
    elif browser == "EDGE":
        # Set options class to configure Edge
        options = EdgeOptions()
        # Check for observing the web-driver's actions in the web browser
        if enable_headless == False:
            # Set web browser option to run with user-interface
            pass
        else:
            # Set web browser option to run without user-interface
            options.add_argument("headless")
        # Ignore error messages `Failed to read descriptor from node connection: A device attached to the system is not functioning` from CLI
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # Launch web browser with options
        driver = webdriver.Edge(options=options)
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

# Used for testing with `python src/espn.py`
if __name__ == "__main__":
    # Get Player's trends dictionary from function above
    data = espn_trends()
    # Print Player trends data
    print(data)
