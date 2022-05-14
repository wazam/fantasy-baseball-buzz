import requests
from ratelimit import limits, RateLimitException, sleep_and_retry


calls_per_pd = 1
pd_time_secs = 1


@sleep_and_retry
@limits(calls= calls_per_pd, period= pd_time_secs)
def make_ratelimited_request(url, headers):
    resp = requests.get(url, headers= headers)
    return resp
