import pandas as pd
import numpy as np
import mysqlaccess as mdb
import datetime 

if __name__ == '__main__':
    x = mdb.load_min_data_to_df('fut_min','m1501',datetime.date(2014,9,1),datetime.date(2014,11,5),minid_start=1501, minid_end=2059)
	y = mdb.load_min_data_to_df('fut_min','RM501',datetime.date(2014,9,1),datetime.date(2014,11,5),minid_start=1501, minid_end=2059)
	spd = x.close - y.close
	