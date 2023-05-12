from bs4 import BeautifulSoup
from util_ratelimit import ratelimit_get_url

headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"}


# Returns results from web page
def beautifulsoup_scrape(url_import, find_type, find_name, find_attrib, find_href):
    response = ratelimit_get_url(url_import, headers)
    soup = BeautifulSoup(markup=response.content, features='html.parser')
    results = beautifulsoup_find(soup, find_type, find_name, find_attrib, find_href)
    return results


# Returns results from web page
def beautifulsoup_find(soup_import, find_type, find_name, find_attrib, find_href):
    if find_type == 'all':
        if find_attrib == '':
            results = soup_import.find_all(find_name, href=find_href)
        else:
            results = soup_import.find_all(find_name, class_=find_attrib, href=find_href)
    else:
        if find_attrib == '':
            results = soup_import.find(find_name, href=find_href)
        else:
            results = soup_import.find(find_name, class_=find_attrib, href=find_href)
    return results


# Tests with `pipenv run python src/util_beautifulsoup.py`
if __name__ == '__main__':
    url = 'http://baseball.fantasysports.yahoo.com/b1/buzzindex'
    print('\n', 'beautifulsoup_scrape()', '\n', beautifulsoup_scrape(url, 'all', 'a', 'Navtarget', True)[46::])
