import datetime
from pandas.core.frame import DataFrame
from sqlalchemy import create_engine
from Constants import Constants as const
from psycopg2 import sql
from Credentials import Credentials as Auth
import pandas as pd
import psycopg2


class DbManagement:
    CONNECTION_PATH = '***REMOVED***'

    def __init__(self):
        self.psy_copg_connection = psycopg2.connect(database="brain", user='postgres', password= Auth.DB_PASS)
        self.sql_alch_connection = create_engine(self.CONNECTION_PATH).connect()


    def reset(self, data:DataFrame, table_name:str = "Data") -> None:
        try:
            data.to_sql(con = self.sql_alch_connection, name = table_name, if_exists = 'replace')
        except:
            SQL = sql.SQL("""CREATE TABLE {table} (ex1 INTEGER,ex2 TEXT);""").format(table=sql.Identifier(table_name))
            self.__execute_sql((),SQL)
            self.psy_copg_connection.commit()
            data.to_sql(con=self.sql_alch_connection, name = table_name, if_exists = 'replace')



    def get_nth_row(self, n:int, table_name:str = "Data") -> DataFrame:
        SQL = sql.SQL("SELECT * FROM (SELECT row_number() OVER (ORDER BY index DESC) r, * FROM {}) q WHERE r = %s")
        return self.__get_row_template(n, SQL, table_name)
     


    def get_last_nth_rows(self, n:int, table_name:str = "Data") -> DataFrame:
        SQL = sql.SQL("SELECT * FROM (SELECT row_number() OVER (ORDER BY index DESC) r, * FROM {}) q WHERE r <= %s")
        return self.__get_row_template(n, SQL, table_name)



    def get_nbr_of_rows(self, table_name:str = "Data") -> int:
        return self.get_previous_row(table_name).at[0, const.INDEX]



    def append_row(self,data:DataFrame, table_name:str = "Data"):
        data.to_sql(con = self.sql_alch_connection, name = table_name, if_exists = 'append')
    
    

    def update_col_at_date(self, dateTime, value, SQL, column_name, table_name = "Data"):
        SQL = sql.SQL("""UPDATE {table} SET {column_name} = %s where "Datetime" = %s""").format(column_name=sql.Identifier(column_name),table=sql.Identifier(table_name))
        self.__execute_sql((dateTime, value),SQL)
        self.psy_copg_connection.commit()



    def get_previous_row(self, table_name:str = "Data") -> DataFrame:
        return self.get_nth_row(1, table_name)
    
    

    def get_row_at_date(self, dateTime:datetime, table_name:str = "Data") -> DataFrame:
        SQL = sql.SQL("""SELECT * FROM {table} WHERE "Datetime" = %s""").format(table=sql.Identifier(table_name))
        cursor = self.__execute_sql( (dateTime,), SQL)
        result = cursor.fetchall()
        return self.__to_data_frame(result)



    def get_row_at_index(self, index:int, table_name:str = "Data") -> DataFrame:
        SQL = sql.SQL("""SELECT * FROM {table} WHERE "index" = %s""").format(table=sql.Identifier(table_name))
        cursor = self.__execute_sql((index,), SQL)
        result = cursor.fetchall()
        return self.__to_data_frame(result)



    def get_table(self, table_name:str = "Data") -> DataFrame:
        return pd.read_sql_table(table_name, self.sql_alch_connection)



    def __create_cursor(self):
        cursor = self.psy_copg_connection.cursor()
        return cursor
    


    def __to_data_frame(self, data:list[tuple]) -> DataFrame:
        return DataFrame(data, columns=['index'] + const.BASE_VALUES + const.ACTIVE_INDICATORS)



    def __execute_sql(self, SQL_arguments:tuple, SQL):
        cursor = self.__create_cursor()
        cursor.execute(SQL, SQL_arguments)
        return cursor



    def __get_row_template(self,n:int, SQL, table_name:str) -> DataFrame:
        SQL = SQL.format(sql.Identifier(table_name))
        cursor = self.__execute_sql((n,), SQL)
        result = cursor.fetchall()
        frame = DataFrame(result,columns=['rem','index'] + const.BASE_VALUES + const.ACTIVE_INDICATORS)
        frame = frame.drop(columns=['rem'])
        return frame