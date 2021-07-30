class Constants:

    TICKERS = ['AAPL', 'TSLA', 'GME']

    #Different ticker settings
    RSI_UPPER_BOUND         = 60
    RSI_LOWER_BOUND         = 40
    RSI_PERIOD              = 12
    LONG_EMA                = 26
    SHORT_EMA               = 12
    RSI_SMOOTH_EMA_PERIOD   = 3
    TICKER_INTERVAL         = 15 #minutes
    TICKER_PERIOD           = 60 #days 
    RR_RATIO                = 1.5
    
    INDEX             = "index"
    DATETIME          = "Datetime"
    OPEN_INDEX        = "Open"
    HIGH_INDEX        = "High"
    LOW_INDEX         = "Low"
    CLOSE_INDEX       = "Close"
    ADJ_CLOSE_INDEX   = "Adj Close"
    VOLUME_INDEX      = "Volume"

    MACD_INDEX          = "MACD"
    SIGNAL_INDEX        = "Signal"
    MACD_DIFF_INDEX     = "MACD Diff"
    RSI_SMOOTH_INDEX    = "Ema %s(Rsi %s)"%(RSI_SMOOTH_EMA_PERIOD,RSI_PERIOD)
    RSI_INDEX           = "Rsi %s"%(RSI_PERIOD)
    EMA_Short_INDEX     = "Ema %s"%(SHORT_EMA)
    EMA_Long_INDEX      = "Ema %s"%(LONG_EMA)
    EMA_RSI_INDEX       = "Ema %s(Rsi %s)"%(RSI_SMOOTH_EMA_PERIOD,RSI_PERIOD)
    EMA_200_INDEX       = "Ema 200"
    EMA_100_INDEX       = "Ema 100"


    POSITION_NONE       = "NONE"
    POSITION_HOLD       = "HOLD"

    ACTIVE_INDICATORS = [RSI_INDEX, EMA_Long_INDEX, EMA_Short_INDEX, EMA_100_INDEX, EMA_200_INDEX,
                         MACD_INDEX, SIGNAL_INDEX, MACD_DIFF_INDEX, RSI_SMOOTH_INDEX]

    BASE_VALUES = [DATETIME, OPEN_INDEX, HIGH_INDEX, LOW_INDEX, CLOSE_INDEX, ADJ_CLOSE_INDEX, VOLUME_INDEX]



