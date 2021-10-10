from Settings import Settings as st
class Constants:
    
    INDEX       = "index"
    DATETIME    = "Datetime"
    OPEN        = "Open"
    HIGH        = "High"
    LOW         = "Low"
    CLOSE       = "Close"
    ADJ_CLOSE   = "Adj Close"
    VOLUME      = "Volume"

    MACD          = "MACD"
    SIGNAL        = "Signal"
    MACD_DIFF     = "MACD Diff"
    RSI_SMOOTH    = "Ema %s(Rsi %s)"%(st.RSI_SMOOTH_EMA_PERIOD, st.RSI_PERIOD)
    RSI           = "Rsi %s"%(st.RSI_PERIOD)
    EMA_Short     = "Ema %s"%(st.SHORT_EMA)
    EMA_Long      = "Ema %s"%(st.LONG_EMA)
    EMA_RSI       = "Ema %s(Rsi %s)"%(st.RSI_SMOOTH_EMA_PERIOD, st.RSI_PERIOD)
    EMA_200       = "Ema 200"
    EMA_100       = "Ema 100"


    POSITION_NONE       = "NONE"
    POSITION_HOLD       = "HOLD"

    ACTIVE_INDICATORS = [RSI, EMA_Long, EMA_Short, EMA_100, EMA_200,
                         MACD, SIGNAL, MACD_DIFF, RSI_SMOOTH]
    BASE_VALUES = [DATETIME, OPEN, HIGH, LOW, CLOSE, ADJ_CLOSE, VOLUME]
    
    ACTIVE_ORDER_COLUMNS =  ["Ticker","Order id","Datetime Buy", "Buy"]
    PREV_ORDER_COLUMNS =   ACTIVE_ORDER_COLUMNS + ["Datetime Sell","Sell"]


