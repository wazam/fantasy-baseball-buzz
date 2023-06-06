import time
from datetime import date
from datetime import timedelta


# Returns date in YYYY-MM-DD format of the day(s) before today
def date_X_days_ago(days):
    date_today = date.today()
    date_days_back = timedelta(days=days)
    date_back = date_today - date_days_back
    return date_back


# Returns time in HH:MM:SS format for use in log terminal with print()
def get_time_for_logs():
    time_now = time.localtime()
    time_now_format = time.strftime("%H:%M:%S", time_now)
    return time_now_format


# Tests with `pipenv run python src/util_datetime.py`
if __name__ == '__main__':
    print('\n', 'get_time_for_logs', '\n', get_time_for_logs())
    print('\n', 'date_X_days_ago()', '\n', date_X_days_ago(7))
