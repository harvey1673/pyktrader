import datetime
import pandas as pd
import pandas.io.sql as psql
import mysql.connector as msql
from mysqlaccess import dbconfig


def get_min_df(inst, startD = datetime.date(2000,1,1), endD = datetime.date.today()):
	conn = msql.connect(**dbconfig)
	
	sqlcmd = "select datetime, open, high, low, close, volume, openInterest from fut_min" + \
			 " where datetime>=%s and datetime<=%s" % (startD., endD) + \
			 " and instID='%s' and min_id>=1500 and min_id<=2115" % inst + \
             " order by datetime" 
	df = psql.frame_query(sqlcmd, con = conn, index_col='datetime')
	conn.close()
	return df
	
def get_daily_df(inst, startD, endD):
	conn = msql.connect(**dbconfig)
	
	sqlcmd = "select datetime, open, high, low, close, volume, openInterest" + \
			 " from fut_min where instID='%s' and min_id>=1500 and min_id<=2115" % inst + \
             " order by datetime" 
	df = psql.frame_query(sqlcmd, con = conn, index_col='datetime')
	conn.close()
	return df