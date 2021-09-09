import pandas
import yfinance as yf  # https://algotrading101.com/learn/yfinance-guide/
from ticker import *
from time import perf_counter
import datetime
import requests


from myUTL import *
from config import *
from yahoo_finance import *

DBG_EN = 0
# session = requests.Session()


def dbg_print(str):
    if (DBG_EN):
        print(str)


def download_complete_data_history(ticker_data, start_date, end_date):
    sd = str(start_date).split(' ')[0]
    ed = str(end_date).split(' ')[0]
    return ticker_data.history(period='1d', start=sd, end=ed)


# input:
#   behavior of start and stop is same as range()
def downtrend(df, start, stop):
    prev_closing_price = df[start]
    for i in range(start + 1, stop):
        # Prev close price must be higher than next close close price
        if (prev_closing_price <= df[i]):
            return False
        prev_closing_price = df[i]
    return True


def bullish_engulfing(dataframe):
    dbg_print(dataframe[['Open', 'Close']].astype('int'))
    data_len = len(dataframe.index)
    mydf_open = dataframe.Open.astype('int')  # save values in int
    mydf_close = dataframe.Close.astype('int')

    # Verify RED candles for n-1 data
    for i in range(data_len - 1):
        if int(mydf_close[i]) >= int(mydf_open[i]):
            # Stock closed higher in n-1 candles
            return False
    # at this point all n-1 candles are red

    # Verify the engulfing candle
    if (mydf_open[data_len - 1] < mydf_close[data_len - 2]) and \
            (mydf_close[data_len - 1] > mydf_open[data_len - 2]):
        return True

    return False


def bullish_thrusting(dataframe):
    dbg_print(dataframe[['Open', 'Close']].astype('int'))
    data_len = len(dataframe.index)
    mydf_open = dataframe.Open.astype('int')  # save values in int
    mydf_close = dataframe.Close.astype('int')

    # Verify RED candles for n-1 data
    for i in range(data_len - 1):
        if int(mydf_close[i]) >= int(mydf_open[i]):
            # Stock closed higher in n-1 candles
            return False
    # at this point all n-1 candles are red

    # Verify the thrusting candle
    if (mydf_open[data_len - 1] > mydf_close[data_len - 2]) and \
            (mydf_close[data_len - 1] > mydf_open[data_len - 2]):
        return True

    return False


def tweezer_bottom(dataframe):
    dbg_print(dataframe[['Open', 'Close']].astype('int'))
    data_len = len(dataframe.index)
    mydf_open = dataframe.Open.astype('int')  # save values in int
    mydf_close = dataframe.Close.astype('int')

    # Verify RED candles for n-2 data
    for i in range(data_len - 2):
        if int(mydf_close[i]) >= int(mydf_open[i]):
            # Stock closed higher in n-1 candles
            return False
    # at this point all n-2 candles are red

    # Verify the tweezer bottom pattern on final 2 candles
    mydf_low = dataframe.Low.astype('int')
    if mydf_low[data_len - 1] == mydf_low[data_len - 2]:
        return True

    return False


# input - dataframe: Pandas dataframe
def bullish_engulfing_old(dataframe):
    WINDOW_SZ = 3
    engulfing_condition = True
    print(dataframe[['Open', 'Close']])
    # print(dataframe.Close)
    for start_day in range(len(dataframe.index)):
        if (len(dataframe.index) - start_day + 1) < WINDOW_SZ:  # plus 1 because last day is inclusive
            # We have reached end of our data set
            break
        # mydf = dataframe[start:start+WINDOW_SZ] # slice rows 1 to 3

        # verify downtrend
        mydf_close = dataframe.Close
        if downtrend(mydf_close, start_day,
                     start_day + WINDOW_SZ - 1):  # minus 1 because last candle may be engulfing candle
            dbg_print("downtrend present for start_day" + str(start_day) + " " + str(mydf_close[start_day]))

        # Verify WINDOW-1 red candles. i.e. open lower than close
        mydf = dataframe[start_day:start_day + WINDOW_SZ]  # slice x:y non inclusive.
        mydf_open = dataframe.Open[start_day:start_day + WINDOW_SZ]
        mydf_close = dataframe.Close[start_day:start_day + WINDOW_SZ]
        print(" ")
        # print(dataframe[['Open', 'Close']][start_day:start_day + WINDOW_SZ])
        for i in range(WINDOW_SZ - 1):
            if mydf_close[i] < mydf_open[i]:
                engulfing_condition = False
                break

        if engulfing_condition == True:
            dbg_print("engulfing present for start_day" + str(start_day))

        # print(mydf)


def back_test(test_bullish_engulfing=False,
              test_bullish_thrusting=False,
              test_tweezer_bottom=False):

    if test_bullish_engulfing == False and \
            test_bullish_thrusting == False and \
            test_tweezer_bottom == False:
        print("ERROR: Select a pattern to back test. Exiting...")
        exit()

    global session
    WINDOW_SZ = 4
    start = perf_counter()
    total_trades = 0
    trades_hit_stop_loss = 0
    trade_list = list()  # this list will hold all the trades for all stocks
    stock_list = snp500#{'ADANIPORTS': 'Adani'}
    for tkr in stock_list:  # Loop for every stock
        print(stock_list[tkr])  # For progress update.

        dt = increment_next_weekday(datetime.datetime(2021, 1, 1))  # Very first day for back test
        date_till = str(dt).split(' ')[0]

        # Last day is 5 day before today because the trades after that haven't completed.
        # +1 if there has been a holiday in between.
        last_date_const = update_next_weekday(datetime.datetime.today(), 5+1, decrement=True)

        # Download the complete data frame for stock price history.
        complete_data_history = get_price_history_data(tkr,
                                                       dt - datetime.timedelta(days=10),
                                                       datetime.datetime.today())
        if complete_data_history.empty:
            continue

        # This loop analyzes the complete data frame for all occurrence for trade patterns
        while dt < last_date_const:  # Loop for whole year for 4 day window

            # start date of swing trade time frame/window
            date_start = str(update_next_weekday(dt, WINDOW_SZ - 1, decrement=True)).split(' ')[0]

            # print('start-' + date_start)
            # print('end-' + date_till)

            tkrDf = complete_data_history[date_start:date_till]

            # Sanity check the data received
            tkrDf = sanity_check(tkrDf)
            # dbg_print(tkrDf)

            while len(tkrDf.index) < WINDOW_SZ and dt < last_date_const:
                # due to holidays, interested data frame may not have data equal
                # to window size. So increment dt and date_till by one
                dt = increment_next_weekday(dt)
                date_till = str(dt).split(' ')[0]
                tkrDf = complete_data_history[date_start:date_till]
            # print(tkrDf)

            # Sanity check data size again.
            if len(tkrDf.index) < WINDOW_SZ or dt >= last_date_const:
                # Date not present in data frame. This would happen if we have
                # reached end of the dataframe. Exit out of while loop
                break

            pattern_condition = False
            if not tkrDf.empty and test_bullish_engulfing:
                pattern_condition = bullish_engulfing(tkrDf)
            if not tkrDf.empty and test_bullish_thrusting:
                pattern_condition = bullish_thrusting(tkrDf)
            if not tkrDf.empty and test_tweezer_bottom:
                pattern_condition = tweezer_bottom(tkrDf)

            if not tkrDf.empty and pattern_condition:
                # trade day, stock name, buy@, stop loss, buy price, sell price, Profit/Loss, Reward/Risk
                # trade day - day you purchase the stock.
                # Risk = buy price - stop loss. i.e. the amt of money we can loss on a trade
                # Reward = profit on the trade
                trade_day = str(increment_next_weekday(dt)).split(' ')[0]
                buy_at_price = tkrDf.Close[len(tkrDf.index) - 1]
                stop_loss = 0
                # print(tkrDf[['Open', 'Close', 'High', 'Low']])
                if test_bullish_engulfing:
                    stop_loss = tkrDf.Open[len(tkrDf.index) - 1]
                elif test_bullish_thrusting:
                    stop_loss = tkrDf.Open[len(tkrDf.index) - 2]
                elif test_tweezer_bottom:
                    stop_loss = tkrDf.Low[len(tkrDf.index) - 1]

                dt_plus_five = update_next_weekday(dt, 5, increment=True)
                date_till_plus_five = str(dt_plus_five).split(' ')[0]
                # print(date_till_plus_five)

                tkrDf = complete_data_history[trade_day:date_till_plus_five]
                while len(tkrDf.index) < 5 and dt_plus_five < last_date_const:
                    # due to holidays, interested data frame may not have data equal
                    # to window size. So increment dt and date_till by one
                    dt_plus_five = increment_next_weekday(dt_plus_five)
                    date_till_plus_five = str(dt_plus_five).split(' ')[0]
                    tkrDf = complete_data_history[trade_day:date_till_plus_five]
                # print(tkrDf)

                # Sanity check data
                if len(tkrDf.index) < 5 or dt_plus_five >= last_date_const:
                    # Date not present in data frame. This would happen if we have
                    # reached end of the dataframe. Exit out of while loop
                    break

                actual_buy_price = tkrDf.Open[0]  # Open price of first day
                if actual_buy_price > stop_loss:
                    # Actual buy price must be greater than the stop loss.
                    # If we are already below stop loss then the buy order will not proceed. I think...
                    total_trades = total_trades + 1
                    #
                    # Let's determine sell price for this trade
                    #
                    sell_price = 0
                    stop_loss_triggered = False
                    # Sell could be triggered by stop loss
                    for low_price in tkrDf.Low:
                        if low_price < stop_loss:
                            # we hit stop loss for this trade
                            trades_hit_stop_loss += 1
                            sell_price = stop_loss
                            stop_loss_triggered = True
                            break
                    # Stop loss not triggered, so we sell on 5th day's close
                    if not stop_loss_triggered:
                        sell_price = tkrDf.Close[len(tkrDf.index) - 1]

                    profit_loss = sell_price - actual_buy_price
                    risk_reward = None
                    if profit_loss > 0:
                        # risk_reward only makes sense when we made a profit
                        risk_reward = profit_loss / (actual_buy_price - stop_loss)

                    tp_list = [trade_day,
                               stock_list[tkr] + "(" + tkr + ")",
                               buy_at_price,
                               stop_loss,
                               actual_buy_price,
                               sell_price,
                               profit_loss,
                               risk_reward]
                    trade_list.append(tp_list)

            # increment dt and date_till by one
            dt = increment_next_weekday(dt)
            date_till = str(dt).split(' ')[0]

    print("Elapsed time in sec:", perf_counter() - start)
    print("Total trades: " + str(total_trades))
    print("trades_hit_stop_loss: " + str(trades_hit_stop_loss))
    dataframe = pandas.DataFrame(trade_list,
                                 columns=['Trade Day',
                                          'Name',
                                          'Buy@ $',
                                          'Stop Loss$',
                                          'Buy Price$',
                                          'Sell Price$',
                                          'Profit/Loss',
                                          'Reward/Risk'])
    # pandas.set_option("display.max_rows", None, "display.max_columns", None)
    pandas.set_option("display.max_rows", None)
    print(dataframe)
    dataframe.to_excel("output.xlsx")


def find_trades_today():
    start = perf_counter()
    bullish_engulfing_list = list()
    bullish_thrusting_list = list()
    tweezer_bottom_list = list()
    for ticker in snp500:
        # get data on this ticker
        tickerData = yf.Ticker(ticker)

        # get the historical prices for this ticker
        # History provides: Open, High, Low, Close, Volume, Dividends, Stock Splits
        tickerDf = tickerData.history(period='1d', start='2021-8-31', end='2021-9-4')  # end date non inclusive
        # tickerDf = tickerData.history(period='1d', interval='5d')
        if tickerDf.empty:
            continue
        if bullish_engulfing(tickerDf):
            temp_list = [snp500[ticker], tickerDf.Close[len(tickerDf.index) - 1],
                         tickerDf.Open[len(tickerDf.index) - 1]]
            bullish_engulfing_list.append(temp_list)

        if bullish_thrusting(tickerDf):
            temp_list = [snp500[ticker], tickerDf.Close[len(tickerDf.index) - 1],
                         tickerDf.Open[len(tickerDf.index) - 2]]
            bullish_thrusting_list.append(temp_list)

        if tweezer_bottom(tickerDf):
            temp_list = [snp500[ticker], tickerDf.Close[len(tickerDf.index) - 1],
                         tickerDf.Low[len(tickerDf.index) - 1]]
            tweezer_bottom_list.append(temp_list)

    print("Elapsed time in sec:", perf_counter() - start)

    print("Bullish engulfing list")
    if bullish_engulfing_list:
        df1 = pandas.DataFrame(bullish_engulfing_list, columns=['Stock', 'Buy $', 'Stop Loss $'])
        print(df1)

    print("Bullish thrusting list")
    if bullish_thrusting_list:
        df2 = pandas.DataFrame(bullish_thrusting_list, columns=['Stock', 'Buy $', 'Stop Loss $'])
        print(df2)

    print("Tweezer bottom pattern list")
    if tweezer_bottom_list:
        df3 = pandas.DataFrame(tweezer_bottom_list, columns=['Stock', 'Buy $', 'Stop Loss $'])
        print(df3)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    back_test(test_bullish_engulfing=True)
    # df = get_price_history_data('MMM', '2021-4-2', '2021-4-7')
    # print(df[['high', 'low', 'open', 'close']])





