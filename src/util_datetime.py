import time
from datetime import date
from datetime import timedelta


# Returns the date in YYYY-MM-DD format of the day(s) before today
def date_X_days_ago(days):
    date_today = date.today()
    date_days_back = timedelta(days=days)
    date_back = date_today - date_days_back
    return date_back


# Returns time in HH:MM:SS format for use in log terminal with print()
def get_time_for_logs():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time


# Tests with `pipenv run python src/util_datetime.py`
if __name__ == '__main__':
    days_back = 7
    print('\n', days_back, ' day(s) ago the date was ', date_X_days_ago(days_back), '.', sep='')
