from datetime import date
from datetime import timedelta

# Returns the date in YYYY-MM-DD format of the day(s) before today 
def days_before_today(days_back):
    date_today = date.today()
    date_days_back = timedelta(days = days_back)
    date_back = date_today - date_days_back
    return date_back


# Used for testing with `pipenv run python src/utils/my_datetime.py`
if __name__ == "__main__":
    days_back = 7
    print('\n', days_back, ' day(s) ago the date was ', days_before_today(days_back), '.', sep="")
