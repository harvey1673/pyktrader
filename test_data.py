import data_saver
import tushare as ts
import datetime
import pandas as pd
import mysql.connector
import misc
import mysqlaccess as db
import os

def save_tick_data(tday, folder = '', tick_id = 300000):
    all_insts = data_saver.filter_main_cont(tday)
    cnx = mysql.connector.connect(**misc.mysqlaccess.dbconfig)
    for inst in all_insts:
        stmt = "select * from fut_tick where instID='{prod}' and date='{cdate}' and tick_id>='{tick}'".format(prod=inst, cdate=tday.strftime('%Y-%m-%d'), tick = tick_id)
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
            stmt = "load data local infile '{data_file}' replace into table fut_tick fields terminated by ',';".format(data_file = data_file)
            cursor.execute( stmt )
            cnx.commit()
            print inst
    cnx.close()
    return

def import_datayes_daily_data(start_date, end_date, cont_list = [], is_replace = False):
    numdays = (end_date - start_date).days + 1
    date_list = [start_date + datetime.timedelta(days=x) for x in range(0, numdays) ]
    date_list = [ d for d in date_list if (d.weekday()< 5) and (d not in misc.CHN_Holidays)]
    for d in date_list:
        cnt = 0
        dstring = d.strftime('%Y%m%d')
        ts.set_token(misc.datayes_token)
        mkt = ts.Market()
        df = mkt.MktFutd(tradeDate = dstring)
        if len(df.ticker) == 0:
            continue
        for cont in df.ticker:
            if (len(cont_list) > 0) and (cont not in cont_list):
                continue
            data = df[df.ticker==cont]
            if len(data) == 0:
                print 'no data for %s for %s' % (cont, dstring)
            else:
                data_dict = {}
                data_dict['date']  = d
                data_dict['open']  = float(data.openPrice)
                data_dict['close'] = float(data.closePrice)
                data_dict['high']  = float(data.highestPrice)
                data_dict['low'] = float(data.lowestPrice)
                data_dict['volume'] = int(data.turnoverVol)
                data_dict['openInterest'] = int(data.openInt)
                if data_dict['volume'] > 0:
                    cnt += 1
                    db.insert_daily_data(cont, data_dict, is_replace = is_replace, dbtable = 'fut_daily')
        print 'date=%s, insert count = %s' % (d, cnt)

if __name__ == '__main__':
    print
