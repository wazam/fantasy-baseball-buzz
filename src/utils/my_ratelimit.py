from requests import get
from ratelimit import limits, sleep_and_retry

calls_per_pd = 1
pd_time_secs = 1


# Returns web page request with rate-limited retries
@sleep_and_retry
@limits(calls=calls_per_pd, period=pd_time_secs)
def ratelimit_get_url(url, headers):
    response = get(url, headers=headers)
    return response


# Tests with `pipenv run python src/util_ratelimit.py`
if __name__ == '__main__':
    url = 'https://baseball.fantasysports.yahoo.com/b1/buzzindex'
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"}
    html_page = ratelimit_get_url(url, headers)
    # html_text = html_page.text
    # html_doc = html_page.content
    if html_page.status_code == 200:
        print('Success')
    else:
        print('Error')
