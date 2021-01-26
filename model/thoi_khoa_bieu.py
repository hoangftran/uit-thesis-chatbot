from psycopg2 import DatabaseError
import psycopg2
import pandas as pd
import sqlalchemy
import datetime as dt
import pytz
import os
from sqlalchemy import exc

DATABASE_URL = os.environ['DATABASE_URL'] if ("DATABASE_URL" in os.environ) else "postgres://dwyknsoayzoodt:9d86f761e2b76a4477ac162c1122b0f0fac9bab6c8ccd85b39df8b6314d110fc@ec2-34-232-24-202.compute-1.amazonaws.com:5432/d8iru0f59gkdlf"

class ThoiKhoaBieuDB():
    def get_tkb(self, mssv):
        try:
            conn = sqlalchemy.create_engine(DATABASE_URL).connect()
            sql="SELECT * FROM tkb WHERE mssv='{}' ORDER BY lastest_date ASC".format(mssv)
            result=pd.read_sql(sql, conn)

        except exc.SQLAlchemyError as e:
            print('HistoryMssvDB :: check_history_mssv :: ', e)
            result='failed'
        finally:
            conn.close()
            return result