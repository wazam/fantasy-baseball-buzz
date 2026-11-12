import time
import random
import requests
from ratelimit import limits, sleep_and_retry
from bs4 import BeautifulSoup

# Matches the Firefox ESR release in the Buzz image
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"}

# Fail a stalled connection instead of hanging the scrape forever
REQUEST_TIMEOUT_SECONDS = 30

# At most one request per REQUEST_DELAY_SECONDS, GET and POST together, so requests never go out in bursts
REQUEST_DELAY_SECONDS = 5.5
# Each request also waits a random REQUEST_DELAY_MIN to REQUEST_DELAY_MAX seconds, so the gaps aren't regular
REQUEST_DELAY_MIN = 0.5
REQUEST_DELAY_MAX = 1.5


@sleep_and_retry
@limits(calls=1, period=REQUEST_DELAY_SECONDS)
def _send(method, url, **kwargs):
    """Return the response to one request, sent after a random pause of REQUEST_DELAY_MIN to REQUEST_DELAY_MAX seconds."""
    time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
    return requests.request(method, url, timeout=REQUEST_TIMEOUT_SECONDS, **kwargs)


def ratelimit_get_url(url, extra_headers=None, params=None):
    """Return the response to a GET, paced by _send."""
    return _send('GET', url, headers={**HEADERS, **(extra_headers or {})}, params=params)


def ratelimit_post_url(url, json=None, data=None, params=None):
    """Return the response to a POST with a body (json for JSON APIs, data for HTML forms), paced by _send."""
    return _send('POST', url, headers=HEADERS, json=json, data=data, params=params)


def beautifulsoup_scrape(url_import, find_type, find_name, find_attrib, find_href):
    """Fetch a page and return what beautifulsoup_find matches on it, or None on a network error or a non-200 status."""
    try:
        response = ratelimit_get_url(url_import)
    except requests.exceptions.RequestException as e:
        print(f"Network error while accessing {url_import}: {e}")
        return None

    if response.status_code != 200:
        print(f"Failed to fetch URL: {url_import} (Status Code: {response.status_code})")
        return None

    soup = BeautifulSoup(markup=response.content, features='html.parser')
    results = beautifulsoup_find(soup, find_type, find_name, find_attrib, find_href)

    if results:
        # find_all returns a list, find returns one element (whose len() counts its children)
        count = len(results) if find_type == 'all' else 1
        print(f"Successfully scraped {url_import} and found {count} elements.")
    return results


def parse_number(text):
    """Return a table cell's number as an int or float, 0 for dash placeholders, or the text if not a number."""
    text = text.strip()
    if text in ['—', '--', '-']:
        return 0
    number = text.replace(',', '').rstrip('%').lstrip('$')
    for cast in (int, float):
        try:
            return cast(number)
        except ValueError:
            pass
    return text


def beautifulsoup_find(soup_import, find_type, find_name, find_attrib, find_href):
    """Return every match when find_type is 'all', else the first match, or None when nothing matches."""
    if not soup_import:
        print("Soup object is None.")
        return None

    find_method = soup_import.find_all if find_type == 'all' else soup_import.find

    search_params = {"name": find_name}
    if find_attrib:
        search_params["class_"] = find_attrib
    if find_href:
        search_params["href"] = find_href

    results = find_method(**search_params)

    if results:
        return results
    else:
        print(f"No elements found for {find_name} with class={find_attrib} and href={find_href}.")
        return None


# Tests with `docker exec buzz ./.venv/bin/python src/util_beautifulsoup.py`
if __name__ == '__main__':
    url = 'https://baseball.fantasysports.yahoo.com/b1/buzzindex'
    scraped_data = beautifulsoup_scrape(url, 'all', 'a', 'Navtarget', True)

    if scraped_data:
        print('\n', 'beautifulsoup_scrape()', '\n', scraped_data[46::])
