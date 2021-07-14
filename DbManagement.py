from typing import List
from Indicators import Indicators
from pandas.core.frame import DataFrame
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from Constants import Constants as const

class DbManagement:
    psyCopgConn = psycopg2.connect(database="brain", user='postgres', password='***REMOVED***')
    conn_path = '***REMOVED***'
    sqlAlchConn = create_engine(conn_path).connect()
    ind:Indicators = Indicators()
    def __init__(self, marketAPI):
        self.marketAPI = marketAPI
        

    def reset(self,data:DataFrame):
        data.to_sql(con=self.sqlAlchConn, name='Data', if_exists='replace')

    def __createCursor(self):
        curr = self.psyCopgConn.cursor()
        return curr

    def update(self): # MUST FIX
        curr = self.__createCursor()
        curr.execute("""SELECT * FROM "Data" ORDER BY index DESC LIMIT 1;""")
        result = curr.fetchall()
        lastEma5 = result[0][9] 
        lastEma12 = result[0][10]
        requestDate = result[0][1]
        data:DataFrame = self.marketAPI.getDataSince(requestDate).iloc[1: , :] #For API-bug giving first index Volume = 0
        newEma5 = self.ind.updateEma(data,const.SHORT_EMA,lastEma5)
        newEma12 = self.ind.updateEma(data,const.LONG_EMA,lastEma12)   
        newRsi:DataFrame =self.ind.rsiInit(self.getLastNthRow(150).iloc[::-1].drop(columns=['index',const.RSI_INDEX,const.EMA_Long_INDEX,const.EMA_Short_INDEX]).append(data),5)[150:]
        newRsi.reset_index(inplace=True)
        data.reset_index(inplace=True)
        res = pd.concat([data.drop(columns='index'),newRsi.drop(columns='index'),newEma5,newEma12],axis=1)
        res.index = range(result[0][0]+1,result[0][0]+len(res)+1) #Configure the indexes of the new values
        self.appendRow(res)



       
    def getNbrOfRows(self):
        self.getPreviousRow()[const.INDEX].tolist()[0]

    def appendRow(self,data:DataFrame):
        data.to_sql(con=self.sqlAlchConn, name='Data', if_exists='append')
    
    

    
    def updateColumnAtDate(self,dateTime,value,SQL):
        curr = self.__createCursor()
        SQL = """UPDATE Data SET "Ema" = %s WHERE "Datetime" = %s;"""
        curr.execute(SQL, (value,dateTime,))
        self.psyCopgConn.commit()

    def updateEmaAtDate(self,dateTime,value):
        self.updateColumnAtDate(dateTime,value,"""UPDATE "Data" SET "Ema" = %s WHERE "Datetime" = %s;""")
    
    def updateRsiAtDate(self,dateTime,value):
        self.updateColumnAtDate(dateTime,value,"""UPDATE "Data" SET "Rsi" = %s WHERE "Date" = %s;""")

    def getPreviousRow(self) -> DataFrame:
        return self.getNthRow(1)
    
    
    def getNthRow(self,n:int) -> DataFrame:
        curr = self.__createCursor()
        SQL = """SELECT * FROM (SELECT row_number() OVER (ORDER BY index DESC) r, * FROM "Data") q
WHERE r = %s"""
        curr.execute(SQL,(n,))
        result = curr.fetchall()
        frame = DataFrame(result,columns=['rem','index','Datetime','Open', 'High', 'Low', 'Close', 'Adj Close','Volume',
                                        const.RSI_INDEX,const.EMA_Long_INDEX, const.EMA_Short_INDEX,const.MACD_LINE_INDEX,
                                        const.SIGNAL_LINE_INDEX,const.MACD_HISTOGRAM_INDEX])
        frame = frame.drop(columns=['rem'])

        return frame
    
    def getLastNthRow(self,n:int) -> DataFrame:
        curr = self.__createCursor()
        SQL = """SELECT * FROM (SELECT row_number() OVER (ORDER BY index DESC) r, * FROM "Data") q
WHERE r <= %s"""
        curr.execute(SQL,(n,))
        result = curr.fetchall()
        frame = DataFrame(result,columns=['rem','index','Datetime','Open', 'High', 'Low', 'Close', 'Adj Close','Volume',
                                        const.RSI_INDEX,const.EMA_Long_INDEX, const.EMA_Short_INDEX,const.MACD_LINE_INDEX,
                                        const.SIGNAL_LINE_INDEX,const.MACD_HISTOGRAM_INDEX])
        frame = frame.drop(columns=['rem'])

        return frame
    

    def getRowAtDate(self, dateTime):
        curr = self.__createCursor()
        SQL = """SELECT * FROM "Data" WHERE "Datetime" = (%s);""" # Note: no quotes
        curr.execute(SQL, (dateTime,)) # Note: no % operator
        result = curr.fetchall()
        frame = DataFrame(result,columns=['index','Datetime','Open', 'High', 'Low', 'Close', 'Adj Close','Volume',
                                        const.RSI_INDEX,const.EMA_Long_INDEX, const.EMA_Short_INDEX,const.MACD_LINE_INDEX,
                                        const.SIGNAL_LINE_INDEX,const.MACD_HISTOGRAM_INDEX])
        return frame

    def getRowAtIndex(self, index):
        curr = self.__createCursor()
        SQL = """SELECT * FROM "Data" WHERE "index" = (%s);""" # Note: no quotes
        curr.execute(SQL, (index,)) # Note: no % operator
        result = curr.fetchall()
        frame = DataFrame(result,columns=['index','Datetime','Open', 'High', 'Low', 'Close', 'Adj Close','Volume',
                                        const.RSI_INDEX,const.EMA_Long_INDEX, const.EMA_Short_INDEX,const.MACD_LINE_INDEX,
                                        const.SIGNAL_LINE_INDEX,const.MACD_HISTOGRAM_INDEX])
        return frame

    
    def tableToDataFrame(self,tableName)->DataFrame:
        return pd.read_sql_table(tableName,self.sqlAlchConn)
        



        










