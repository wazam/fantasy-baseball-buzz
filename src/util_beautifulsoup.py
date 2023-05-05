from bs4 import BeautifulSoup
from util_ratelimit import ratelimit_get_url

headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"}


# Return class tag(s) from web page
def beautifulsoup_scrape_class(url_import, find_all, find_name, find_attrib, href):
    response = ratelimit_get_url(url_import, headers)
    soup = BeautifulSoup(markup=response.content, features='html.parser')
    results = beautifulsoup_find_class(soup, find_all, find_name, find_attrib, href)
    return results


# Return class tag(s) from soup
def beautifulsoup_find_class(soup, find_all, find_name, find_attrib, href):
    if find_all == 'all':
        results = soup.find_all(find_name, class_=find_attrib, href=href)
    else:
        results = soup.find(find_name, class_=find_attrib, href=href)
    return results


# Return search result(s) from web page
def beautifulsoup_scrape(url_import, find_all, find_name, href):
    response = ratelimit_get_url(url_import, headers)
    soup = BeautifulSoup(markup=response.content, features='html.parser')
    results = beautifulsoup_find(soup, find_all, find_name, href)
    return results


# Return search result(s) from soup
def beautifulsoup_find(soup_import, find_all, find_name, href):
    if find_all == 'all':
        results = soup_import.find_all(find_name, href=href)
    else:
        results = soup_import.find(find_name, href=href)
    return results


# Tests with `pipenv run python src/util_beautifulsoup.py`
if __name__ == '__main__':
    url = 'http://baseball.fantasysports.yahoo.com/b1/buzzindex'
    print('\n', 'beautifulsoup_scrape_class()', '\n', beautifulsoup_scrape_class(url, 'all', 'a', 'Navtarget', True)[46::])
