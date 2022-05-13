import requests
from bs4 import BeautifulSoup


# Scrape web_page for class_
def scrape_class(url, headers, all, name, attrib, href):
    page = requests.get(url, headers= headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = find_class(soup, all, name, attrib, href)
    return results


# Find in results_page or html_soup for class_
def find_class(soup, all, name, attrib, href):
    if all == 'all':
        results = soup.find_all(name, class_= attrib, href= href)
    else:
        results = soup.find(name, class_= attrib, href= href)
    return results


# Find in results_page or html_soup for class_
def find(soup, all, name, href):
    if all == 'all':
        results = soup.find_all(name, href= href)
    else:
        results = soup.find(name, href= href)
    return results
