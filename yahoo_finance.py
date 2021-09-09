from yahoofinancials import YahooFinancials
import pandas


# end_date not exclusive
def get_price_history_data(ticker, start_date, end_date):
    sd = str(start_date).split(' ')[0]
    ed = str(end_date).split(' ')[0]

    yahoo_financials = YahooFinancials(ticker)
    historical_stock_prices = yahoo_financials.get_historical_price_data(sd, ed, 'daily')

    data_frame = pandas.DataFrame(historical_stock_prices[ticker]['prices'])

    # convert the 'formatted_date' column (it's a string) to datetime type
    datetime_series = pandas.to_datetime(data_frame['formatted_date'])

    # create datetime index passing the datetime series
    datetime_index = pandas.DatetimeIndex(datetime_series.values)

    data_frame = data_frame.set_index(datetime_index)

    # we don't need the following columns anymore
    data_frame.drop('formatted_date', axis=1, inplace=True)
    data_frame.drop('date', axis=1, inplace=True)

    data_frame = data_frame.rename(columns={'open': 'Open', 'close': 'Close', 'high': 'High', 'low': 'Low'})
    # print(data_frame)
    return data_frame
