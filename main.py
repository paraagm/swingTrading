import pandas
import yfinance as yf  # https://algotrading101.com/learn/yfinance-guide/
from ticker import snp500
from time import perf_counter

DBG_EN = 0


def dbg_print(str):
    if (DBG_EN):
        print(str)


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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
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
            temp_list = [snp500[ticker], tickerDf.Close[len(tickerDf.index) - 1], tickerDf.Low[len(tickerDf.index) - 1]]
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

