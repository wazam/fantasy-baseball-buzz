import shutil
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# Fail a stuck page load instead of waiting Selenium's 5 minute default
PAGE_LOAD_TIMEOUT_SECONDS = 60


def webdriver_setup_driver():
    """Return a headless Firefox driver, ready to load a URL."""
    # Firefox and geckodriver come from the Dockerfile's Alpine packages
    firefox_binary = shutil.which('firefox-esr')
    driver_binary = shutil.which('geckodriver')
    missing = [name for name, path in (('firefox-esr', firefox_binary), ('geckodriver', driver_binary)) if not path]
    if missing:
        raise RuntimeError(f'{" and ".join(missing)} not found on PATH (both ship in the Buzz image)')
    # The container has no display, so Firefox always runs headless
    firefox_options = FirefoxOptions()
    firefox_options.add_argument('--headless')
    firefox_options.binary_location = firefox_binary
    driver = webdriver.Firefox(service=FirefoxService(driver_binary), options=firefox_options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_SECONDS)
    return driver


@contextmanager
def webdriver_session():
    """Yield a driver and always quit it, even when scraping raises."""
    driver = webdriver_setup_driver()
    try:
        yield driver
    finally:
        # Closes every window and stops geckodriver
        driver.quit()


# Tests with `docker exec buzz ./.venv/bin/python src/util_webdriver.py`
if __name__ == '__main__':
    with webdriver_session() as driver:
        driver.get('https://github.com')
        print('\n', 'webdriver_session()', '\n', driver.title)
