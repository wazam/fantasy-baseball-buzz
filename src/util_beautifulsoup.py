import os
import time
import random
import requests
from ratelimit import limits, sleep_and_retry
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"}

requests_per_window = int(os.getenv("REQUESTS_PER_WINDOW", 1))
request_delay_seconds = float(os.getenv("REQUEST_DELAY_SECONDS", 5.5))
request_delay_min = float(os.getenv("REQUEST_DELAY_MIN", 0.5))
request_delay_max = float(os.getenv("REQUEST_DELAY_MAX", 1.5))

@sleep_and_retry
@limits(calls=requests_per_window, period=request_delay_seconds)
def ratelimit_get_url(url, headers):
    # Randomized sleep before each request
    delay = random.uniform(request_delay_min, request_delay_max)
    time.sleep(delay)

    response = requests.get(url, headers=headers)
    return response


# Returns results from web page
def beautifulsoup_scrape(url_import, find_type, find_name, find_attrib, find_href):
    """Scrape a web page and extract content based on specified tags."""
    try:
        response = ratelimit_get_url(url_import, headers)

        if response.status_code != 200:
            print(f"Failed to fetch URL: {url_import} (Status Code: {response.status_code})")
            return None

        soup = BeautifulSoup(markup=response.content, features='html.parser')
        results = beautifulsoup_find(soup, find_type, find_name, find_attrib, find_href)

        if results:
            print(f"Successfully scraped {url_import} and found {len(results)} elements.")
        return results

    except requests.exceptions.RequestException as e:
        print(f"Network error while accessing {url_import}: {e}")
        return None

    except Exception as e:
        print(f"Unexpected error during scraping: {e}")
        return None



def beautifulsoup_find(soup_import, find_type, find_name, find_attrib, find_href):
    """Find all matching elements, return None if no elements found."""
    try:
        if not soup_import:
            print("Soup object is None.")
            return None

        # Find logic for 'all' or single elements
        find_method = soup_import.find_all if find_type == 'all' else soup_import.find

        # Build search parameters dynamically
        search_params = {"name": find_name}
        if find_attrib:
            search_params["class_"] = find_attrib
        if find_href:
            search_params["href"] = find_href

        # Perform the search
        results = find_method(**search_params)

        if results:
            return results
        else:
            print(f"No elements found for {find_name} with class={find_attrib} and href={find_href}.")
            return None

    except Exception as e:
        print(f"Error during beautifulsoup_find: {e}")
        return None


# Tests with `pipenv run python src/util_beautifulsoup.py`
if __name__ == '__main__':
    url = 'http://baseball.fantasysports.yahoo.com/b1/buzzindex'
    scraped_data = beautifulsoup_scrape(url, 'all', 'a', 'Navtarget', True)

    if scraped_data:
        print('\n', 'beautifulsoup_scrape()', '\n', scraped_data[46::])