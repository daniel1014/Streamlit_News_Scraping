from dotenv import dotenv_values
from sqlalchemy import create_engine, text
import urllib
import pandas as pd
import pyodbc
import os

class DatabaseConnection:
    def __init__(self):
        config = dotenv_values(".env")
        self.server = os.getenv('Server')
        self.database = os.getenv('Database')
        self.user = os.getenv('User')
        self.password = os.getenv('Pass')

    def read_db_conn_details(self) -> dict:
        params = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={self.server};DATABASE={self.database};UID={self.user};PWD={self.password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30"
        return params

    def df_from_db(self, query: str) -> pd.DataFrame:
        params = self.read_db_conn_details()
        conn_str = "mssql+pyodbc:///?odbc_connect=" + params
        engine = create_engine(conn_str)
        df = pd.read_sql_query(text(query), con=engine.connect())
        return df

    def upload_data_input(self, data: list, table_name: str, username: str):
        cnxn = pyodbc.connect(self.read_db_conn_details())
        cursor = cnxn.cursor()
        schema = 'BMT'

        delete_all_query = f'''
        DELETE FROM {schema}.{table_name}
        WHERE username = ?
        '''
        cursor.execute(delete_all_query, username)

        for record in data:
            insert_query = f'''
                INSERT INTO {schema}.{table_name} (supplier, focus, num_search, username)
                VALUES (?, ?, ?, ?)
            '''
            cursor.execute(insert_query, record['supplier'], record['focus'], record['num_search'], username)

        cnxn.commit()
        cursor.close()
        cnxn.close()

    def upload_data_output(self, data: list, table_name: str, username: str):
        cnxn = pyodbc.connect(self.read_db_conn_details())
        cursor = cnxn.cursor()
        schema = 'BMT'

        delete_all_query = f'''
        DELETE FROM {schema}.{table_name}
        WHERE username = ?
        '''
        cursor.execute(delete_all_query, username)

        for record in data:
            insert_query = f'''
                INSERT INTO {schema}.{table_name} (Supplier, Focus, Title, Date, Description, URL, Username)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(insert_query, record['Supplier'], record['Focus'], record['Title'], record['Date'], record['Description'], record['URL'], username)

        cnxn.commit()
        cursor.close()
        cnxn.close()
