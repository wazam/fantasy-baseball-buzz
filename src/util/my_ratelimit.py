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
