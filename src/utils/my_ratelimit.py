import requests
from ratelimit import limits, sleep_and_retry


calls_per_pd = 1
pd_time_secs = 1


# Returns web page request after utilizing rate-limit protection and retry methods
@sleep_and_retry
@limits(calls = calls_per_pd, period = pd_time_secs)
def make_ratelimited_request(url_import, headers_import):
    response = requests.get(url = url_import, headers = headers_import)
    return response


# Used for testing with `pipenv run python src/utils/my_ratelimit.py` or `pipenv run python -m src.utils.my_ratelimit`
if __name__ == "__main__":
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"}
    html_page = make_ratelimited_request("https://baseball.fantasysports.yahoo.com/b1/buzzindex", headers)
    # html_text = html_page.text
    # html_doc = html_page.content
    if html_page.status_code == 200:
        print("Success")
    else:
        print("Error")
