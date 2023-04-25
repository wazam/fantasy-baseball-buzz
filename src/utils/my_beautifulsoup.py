from bs4 import BeautifulSoup

import src.utils.my_ratelimit as MyR


# Return class tag(s) from web page
def scrape_class(url_import, headers_import, find_all, find_name, find_attrib, href_import):
    response = MyR.make_ratelimited_request(url_import, headers_import)
    soup = BeautifulSoup(markup = response.content, features = 'html.parser')
    results = find_class(soup, find_all, find_name, find_attrib, href_import)
    return results


# Return class tag(s) from soup
def find_class(soup_import, find_all, find_name, find_attrib, href_import):
    if find_all == 'all':
        results = soup_import.find_all(find_name, class_ = find_attrib, href = href_import)
    else:
        results = soup_import.find(find_name, class_ = find_attrib, href = href_import)
    return results


# Return search result(s) from web page
def scrape(url_import, headers_import, find_all, find_name, href_import):
    response = MyR.make_ratelimited_request(url_import, headers_import)
    soup = BeautifulSoup(markup = response.content, features = 'html.parser')
    results = find(soup, find_all, find_name, href_import)
    return results


# Return search result(s) from soup
def find(soup_import, find_all, find_name, href_import):
    if find_all == 'all':
        results = soup_import.find_all(find_name, href = href_import)
    else:
        results = soup_import.find(find_name, href = href_import)
    return results
