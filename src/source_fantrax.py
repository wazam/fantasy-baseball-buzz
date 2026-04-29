from bs4 import BeautifulSoup
import re


##
def fantrax_get(trend_type):
    return None
##


def extract_fantrax_league_id(html):
    soup = BeautifulSoup(html, 'html.parser')
    anchor = soup.find('a', href=True)
    match = re.search(r'/fantasy/league/([^/]+)/', anchor['href'])
    return match.group(1) if match else None


# Tests with `pipenv run python src/source_fantrax.py`
if __name__ == '__main__':
    print('\n', 'fantrax_get(added123)', '\n', fantrax_get('added123'))
