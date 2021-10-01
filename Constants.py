class Constants:
    
    TICKERS = ['AAPL', 'TSLA', 'ERIC']

    #Different ticker settings
    RSI_UPPER_BOUND         = 60
    RSI_LOWER_BOUND         = 40
    RSI_PERIOD              = 12
    LONG_EMA                = 26
    SHORT_EMA               = 12
    RSI_SMOOTH_EMA_PERIOD   = 3
    TICKER_INTERVAL         = 5 #minutes
    TICKER_PERIOD           = 60 #days 
    RR_RATIO                = 1.5
    TICKER_MAX_HOLDINGS     = 1
    
    INDEX             = "index"
    DATETIME          = "Datetime"
    OPEN        = "Open"
    HIGH        = "High"
    LOW         = "Low"
    CLOSE       = "Close"
    ADJ_CLOSE   = "Adj Close"
    VOLUME      = "Volume"

    MACD          = "MACD"
    SIGNAL        = "Signal"
    MACD_DIFF     = "MACD Diff"
    RSI_SMOOTH    = "Ema %s(Rsi %s)"%(RSI_SMOOTH_EMA_PERIOD,RSI_PERIOD)
    RSI           = "Rsi %s"%(RSI_PERIOD)
    EMA_Short     = "Ema %s"%(SHORT_EMA)
    EMA_Long      = "Ema %s"%(LONG_EMA)
    EMA_RSI       = "Ema %s(Rsi %s)"%(RSI_SMOOTH_EMA_PERIOD,RSI_PERIOD)
    EMA_200       = "Ema 200"
    EMA_100       = "Ema 100"


    POSITION_NONE       = "NONE"
    POSITION_HOLD       = "HOLD"

    ACTIVE_INDICATORS = [RSI, EMA_Long, EMA_Short, EMA_100, EMA_200,
                         MACD, SIGNAL, MACD_DIFF, RSI_SMOOTH]
    BASE_VALUES = [DATETIME, OPEN, HIGH, LOW, CLOSE, ADJ_CLOSE, VOLUME]
    
    ACTIVE_ORDER_COLUMNS =  ["Ticker","Order id","Datetime Buy", "Buy", "Stop loss", "Profit take"]
    PREV_ORDER_COLUMNS =   ACTIVE_ORDER_COLUMNS + ["Datetime Sell","Sell"]




