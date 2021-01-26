from psycopg2 import DatabaseError
import pandas as pd
import sqlalchemy
import datetime as dt
import pytz
import os

DATABASE_URL = os.environ['DATABASE_URL'] if ("DATABASE_URL" in os.environ) else "postgres://dwyknsoayzoodt:9d86f761e2b76a4477ac162c1122b0f0fac9bab6c8ccd85b39df8b6314d110fc@ec2-34-232-24-202.compute-1.amazonaws.com:5432/d8iru0f59gkdlf"

class ReportDB():

    def insert_row(self, sender_id, mssv, report_to, report_content, date, status):
        conn=None
        try:
            conn = sqlalchemy.create_engine(DATABASE_URL).connect()
            save_to_db = pd.DataFrame({
                'sender_id': [sender_id],
                'mssv': [mssv],
                'report_to': [report_to],
                'report_content': [report_content],
                'date': [date],
                'status': [status]
            })
            save_to_db.to_sql('report', conn, if_exists='append', index=False)
        except (Exception, DatabaseError) as error:
            print('error while connecting posgre :: {}'.format(error))
        finally:
            conn.close()
            return mssv