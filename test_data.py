import data_saver
import datetime
import pandas as pd
import mysql.connector
import misc
import os

def save_tick_data(tday, folder = ''):
    all_insts = data_saver.filter_main_cont(tday)
    cnx = mysql.connector.connect(**misc.mysqlaccess.dbconfig)
    for inst in all_insts:
        stmt = "select * from fut_tick where instID='{prod}' and date='{cdate}'".format(prod=inst, cdate=tday.strftime('%Y-%m-%d'))
        df = pd.io.sql.read_sql(stmt, cnx)
        df.to_csv(folder + inst + '.csv', header=False, index=False)
    return

def load_tick_data(tday, folder = ''):
    all_insts = data_saver.filter_main_cont(tday)
    cnx = mysql.connector.connect(**misc.mysqlaccess.dbconfig)
    cursor = cnx.cursor()
    for inst in all_insts:
        data_file = folder + inst + '.csv'
        if os.path.isfile(data_file):
            stmt = "load data infile '{data_file}' replace into table fut_tick fields terminated by ','".format(data_file = data_file)
            cursor.execute( stmt )
            print inst
    cnx.close()
    return

if __name__ == '__main__':
    print
