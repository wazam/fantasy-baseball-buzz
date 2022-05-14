from datetime import date
from datetime import timedelta


# Returns the date in YYYY-MM-DD format of the day(s) before today 
def days_before_today(days_back):
    date_today = date.today()
    date_days_back = timedelta(days = days_back)
    date_back = date_today - date_days_back
    return date_back


# ```python src/util/my_datetime.py```
if __name__ == "__main__":
    days_ago = 10
    the_date = days_before_today(days_ago)
    print(the_date, 'was the date', days_ago, 'days ago.')
