import datetime


# date - datetime type
# return date after increment by 1
def increment_next_weekday(date):
    next_weekday_date = date + datetime.timedelta(days=1)
    if next_weekday_date.weekday() == 5:
        # this is Saturday
        next_weekday_date = next_weekday_date + datetime.timedelta(days=2)
    if next_weekday_date.weekday() == 6:
        # this is Sunday
        next_weekday_date = next_weekday_date + datetime.timedelta(days=1)
    return next_weekday_date


# date - datetime type
# return date after decrement by 1
def decrement_prev_weekday(date):
    next_weekday_date = date - datetime.timedelta(days=1)
    if next_weekday_date.weekday() == 5:
        # this is Saturday
        next_weekday_date = next_weekday_date - datetime.timedelta(days=1)
    if next_weekday_date.weekday() == 6:
        # this is Sunday
        next_weekday_date = next_weekday_date - datetime.timedelta(days=2)
    return next_weekday_date


# date - datetime type
# days - number of days to increment or decrement by
# returns date after update
def update_next_weekday(date, days, increment=False, decrement=False):
    if increment == decrement:
        print ("Error: update_next_weekday() - cannot have same value for increment and decrement")
        exit()
    if increment:
        for i in range(days):
            date = increment_next_weekday(date)
    if decrement:
        for i in range(days):
            date = decrement_prev_weekday(date)
    return date


def sanity_check(data_frame):
    if data_frame.isnull().values.any():
        # print(data_frame)
        print("Dropping rows with NaN. New Data Frame is:")
        data_frame = data_frame.dropna()
        # print(data_frame)
    return data_frame

