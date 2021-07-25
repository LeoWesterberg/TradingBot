from Indicators import Indicators
from pandas.core.frame import DataFrame
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from Constants import Constants as const
from psycopg2 import sql
from Credentials import Credentials as Auth


class DbManagement:

    psyCopgConn = psycopg2.connect(database="brain", user='postgres', password= Auth.DB_PASS)
    conn_path = '***REMOVED***'
    sqlAlchConn = create_engine(conn_path).connect()
    ind:Indicators = Indicators()

    def __init__(self, api):
        self.api = api


    def reset(self,data:DataFrame,tableName="Data"):
        try:
            data.to_sql(con=self.sqlAlchConn, name=tableName, if_exists='replace')
        except:
            curr = self.__createCursor()
            SQL = sql.SQL("""CREATE TABLE {table} (ex1 INTEGER,ex2 TEXT);""").format(table=sql.Identifier(tableName))
            curr.execute(SQL, ())
            self.psyCopgConn.commit()
            data.to_sql(con=self.sqlAlchConn, name=tableName, if_exists='replace')




    def getNthRow(self,n:int,tableName="Data") -> DataFrame:
        SQL = sql.SQL("SELECT * FROM (SELECT row_number() OVER (ORDER BY index DESC) r, * FROM {}) q WHERE r = %s")
        return self.__getRowTemplate(n,SQL,tableName)
     
    def getLastNthRow(self,n:int,tableName="Data") -> DataFrame:
        SQL = sql.SQL("SELECT * FROM (SELECT row_number() OVER (ORDER BY index DESC) r, * FROM {}) q WHERE r <= %s")
        return self.__getRowTemplate(n,SQL,tableName)

    def getNbrOfRows(self,tableName="Data"):
        self.getPreviousRow(tableName)[const.INDEX].tolist()[0]

    def appendRow(self,data:DataFrame,tableName="Data"):
        data.to_sql(con=self.sqlAlchConn, name=tableName, if_exists='append')
    
    
    def appendColumnAD(self,dateTime,value,SQL,attr,tableName="Data"):
        curr = self.__createCursor()
        SQL = sql.SQL("""UPDATE {table} SET {attr} = %s where "Datetime" = %s""").format(attr=sql.Identifier(attr),table=sql.Identifier(tableName))
        curr.execute(SQL, (dateTime,value))
        self.psyCopgConn.commit()
        curr = self.__createCursor()
        SQL = sql.SQL("""UPDATE {table} SET {attr} = %s where "Datetime" = %s""").format(attr=sql.Identifier(attr),table=sql.Identifier(tableName))
        curr.execute(SQL, (dateTime,value))
        self.psyCopgConn.commit()


    def getPreviousRow(self,tableName="Data") -> DataFrame:
        return self.getNthRow(1,tableName)
    
    

    def getRowAD(self, dateTime,tableName="Data"):
        curr = self.__createCursor()
        SQL = sql.SQL("""SELECT * FROM {table} WHERE "Datetime" = %s""").format(table=sql.Identifier(tableName))
        curr.execute(SQL, (dateTime,)) # Note: no % operator
        result = curr.fetchall()
        frame = DataFrame(result,columns=['index'] + const.BASE_VALUES + const.ACTIVE_INDICATORS)
        return frame

    def getRowAtIndex(self, index,tableName="Data"):
        curr = self.__createCursor()
        SQL = sql.SQL("""SELECT * FROM {table} WHERE "index" = %s""").format(table=sql.Identifier(tableName))
        curr.execute(SQL, (index,))
        result = curr.fetchall()
        frame = DataFrame(result,columns=['index'] + const.BASE_VALUES + const.ACTIVE_INDICATORS)
        return frame

    
    def tableToDataFrame(self,tableName="Data")->DataFrame:
        return pd.read_sql_table(tableName,self.sqlAlchConn)

################################ PRIVATE FUNCTIONS ##################################
    def __createCursor(self):
        curr = self.psyCopgConn.cursor()
        return curr

    def __getRowTemplate(self,n:int,SQL,tableName) -> DataFrame:
        curr = self.__createCursor()
        SQL = SQL.format(sql.Identifier(tableName))
        curr.execute(SQL,[n])
        result = curr.fetchall()
        frame = DataFrame(result,columns=['rem','index'] + const.BASE_VALUES + const.ACTIVE_INDICATORS)
        frame = frame.drop(columns=['rem'])
        return frame
        






