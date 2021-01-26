from psycopg2 import DatabaseError
import psycopg2
import pandas as pd
import sqlalchemy
import datetime as dt
import pytz
import os
from sqlalchemy import exc

DATABASE_URL = os.environ['DATABASE_URL'] if ("DATABASE_URL" in os.environ) else "postgres://dwyknsoayzoodt:9d86f761e2b76a4477ac162c1122b0f0fac9bab6c8ccd85b39df8b6314d110fc@ec2-34-232-24-202.compute-1.amazonaws.com:5432/d8iru0f59gkdlf"

class HistoryMssvDB():

    def insert_row(self, sender_id, mssv, lastest_date):
        try:
            conn = sqlalchemy.create_engine(DATABASE_URL).connect()
            save_to_db = pd.DataFrame({
                'sender_id': [sender_id],
                'mssv': [mssv],
                'lastest_date': [lastest_date]
            })
            save_to_db.to_sql('history_mssv', conn, if_exists='append', index=False)
        except exc.SQLAlchemyError as e:
            print('HistoryMssvDB :: insert_row :: ', e)
        finally:
            conn.close()
            return mssv
    
    def update_history_mssv(self, sender_id, mssv, lastest_date):
        try:
            engine = sqlalchemy.create_engine(DATABASE_URL)
            sql="UPDATE history_mssv SET mssv='{}', lastest_date='{}' WHERE sender_id='{}'".format(mssv, lastest_date, sender_id)
            with engine.connect() as connection:
                connection.execute(sql)
        except exc.SQLAlchemyError as e:
            print('HistoryMssvDB :: update_history_mssv :: ', e)
        finally:
            connection.close()
            return mssv


    
    def check_history_mssv(self, sender_id):
        try:
            conn = sqlalchemy.create_engine(DATABASE_URL).connect()
            sql="SELECT * FROM history_mssv WHERE sender_id='{}' ORDER BY lastest_date ASC".format(sender_id)
            result=pd.read_sql(sql, conn)

        except exc.SQLAlchemyError as e:
            print('HistoryMssvDB :: check_history_mssv :: ', e)
        finally:
            conn.close()
            return result