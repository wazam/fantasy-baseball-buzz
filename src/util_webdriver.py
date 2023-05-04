import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
# from webdriver_manager.core.utils import read_version_from_cmd, PATTERN  # (used during testing)

headless = int(os.environ.get('SELENIUM_HEADLESS', 1))


# Returns webdriver controlled browser environment, ready for URL and search
def webdriver_setup_driver():
    # Use optional non-headless mode during development with GUI access
    firefox_options = FirefoxOptions()
    if headless == 1:
        firefox_options.add_argument('--headless')  # .add_argument('--no-sandbox')
    # # Returns current version of browser (used during testing)
    # version = read_version_from_cmd('/usr/bin/firefox --version', PATTERN['firefox'])
    # print(version)
    # breakpoint()
    # Firefox install in Dockerfile, manual install req. to run python file w/o Docker
    firefox_options.binary_location = r'/usr/bin/firefox'
    driver_binary = GeckoDriverManager().install()  # .install(version=version)
    driver_service = FirefoxService(driver_binary)
    driver = webdriver.Firefox(service=driver_service, options=firefox_options)
    # # Returns current user-agent from browser (used during testing)
    # user_agent = driver.execute_script('return navigator.userAgent;')
    # headers = {'User-Agent': user_agent}
    # print(headers)
    # breakpoint()
    return driver


# Closes the webdriver elegantly
def webdriver_cleanup_driver(driver):
    driver.close()
    driver.quit()
    return


# Used for testing with `pipenv run python src/util_webdriver.py`
if __name__ == '__main__':
    driver = webdriver_setup_driver()
    print('\n', 'webdriver_setup_driver', '\n', driver.get('https://github.com'))
    print('\n', 'webdriver_cleanup_driver()', '\n', webdriver_cleanup_driver(driver))
