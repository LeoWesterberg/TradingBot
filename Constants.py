class Constants:
    tickers = ['AAPL','TSLA','GME','BTC-USD','ETH-USD']
    STOCK = 'TSLA'
    RSI_UPPER_BOUND = 70
    RSI_LOWER_BOUND = 30
    RSI_PERIOD = 12
    LONG_EMA = 26
    DERIVATIVE_EMA = 40
    SHORT_EMA = 12
    RSI_SMOOTH_EMA_PERIOD = 3

    INDEX = "index"
    DATETIME = "Datetime"
    OPEN_INDEX = "Open"
    HIGH_INDEX = "High"
    LOW_INDEX = "Low"
    CLOSE_INDEX = "Close"
    ADJ_CLOSE_INDEX = "Adj Close"
    VOLUME_INDEX = "Volume"
    MACD_LINE_INDEX = "MACD Line"
    SIGNAL_LINE_INDEX ="Signal Line"
    MACD_HISTOGRAM_INDEX ="MACD Histogram"
    RSI_SMOOTH_INDEX ="Ema %s(Rsi %s)"%(RSI_SMOOTH_EMA_PERIOD,RSI_PERIOD)

    RSI_INDEX = "Rsi %s"%(RSI_PERIOD)
    EMA_Short_INDEX = "Ema %s"%(SHORT_EMA)
    EMA_Long_INDEX = "Ema %s"%(LONG_EMA)

    POSITION_NONE = "NONE"
    POSITION_HOLD = "HOLD"

    

