import data_saver
import tushare as ts
import datetime
import pandas as pd
import mysql.connector as mysqlconn
import misc
import backtest
import os
import urllib2
import pytz
import patoolib
import mysqlaccess as db
import json
from glob import glob
#
# from bs4 import BeautifulSoup
# from datetime import datetime
# from pandas.io.data import DataReader
#
# SITE = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
# START = datetime(1900, 1, 1, 0, 0, 0, 0, pytz.utc)
# END = datetime.today().utcnow()
#
#
# def scrape_list(site):
#     hdr = {'User-Agent': 'Mozilla/5.0'}
#     req = urllib2.Request(site, headers=hdr)
#     page = urllib2.urlopen(req)
#     soup = BeautifulSoup(page)
#
#     table = soup.find('table', {'class': 'wikitable sortable'})
#     sector_tickers = dict()
#     for row in table.findAll('tr'):
#         col = row.findAll('td')
#         if len(col) > 0:
#             sector = str(col[3].string.strip()).lower().replace(' ', '_')
#             ticker = str(col[0].string.strip())
#             if sector not in sector_tickers:
#                 sector_tickers[sector] = list()
#             sector_tickers[sector].append(ticker)
#     return sector_tickers
#
#
# def download_ohlc(sector_tickers, start, end):
#     sector_ohlc = {}
#     for sector, tickers in sector_tickers.iteritems():
#         print 'Downloading data from Yahoo for %s sector' % sector
#         data = DataReader(tickers, 'yahoo', start, end)
#         for item in ['Open', 'High', 'Low']:
#             data[item] = data[item] * data['Adj Close'] / data['Close']
#         data.rename(items={'Open': 'open', 'High': 'high', 'Low': 'low',
#                            'Adj Close': 'close', 'Volume': 'volume'},
#                     inplace=True)
#         data.drop(['Close'], inplace=True)
#         sector_ohlc[sector] = data
#     print 'Finished downloading data'
#     return sector_ohlc
#
#
# def store_HDF5(sector_ohlc, path):
#     with pd.get_store(path) as store:
#         for sector, ohlc in sector_ohlc.iteritems():
#             store[sector] = ohlc
#
#
# def get_snp500():
#     sector_tickers = scrape_list(SITE)
#     sector_ohlc = download_ohlc(sector_tickers, START, END)
#     store_HDF5(sector_ohlc, 'snp500.h5')

def save_tick_data(tday, folder = '', tick_id = 300000):
    all_insts = data_saver.filter_main_cont(tday)
    cnx = mysqlconn.connect(**misc.mysqlaccess.dbconfig)
    for inst in all_insts:
        stmt = "select * from fut_tick where instID='{prod}' and date='{cdate}' and tick_id>='{tick}'".format(prod=inst, cdate=tday.strftime('%Y-%m-%d'), tick = tick_id)
        df = pd.io.sql.read_sql(stmt, cnx)
        df.to_csv(folder + inst + '.csv', header=False, index=False)
    return

def load_tick_data(tday, folder = ''):
    all_insts = data_saver.filter_main_cont(tday)
    cnx = mysqlconn.connect(**misc.mysqlaccess.dbconfig)
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

def extract_rar_data(source, target, extract_src = False):
    if extract_src:
        for file in os.listdir(source):
            if file.endswith(".rar"):
                patoolib.extract_archive(source+file, outdir = target)
    allrar = [y for x in os.walk(target) for y in glob(os.path.join(x[0], '*.rar'))]
    for file in allrar:
        patoolib.extract_archive(file, outdir = target)

def conv_csv_to_sql(target, db_table = 'test_fut_tick'):
    cnx = mysqlconn.connect(**db.dbconfig)
    allcsvs = [y for x in os.walk(target) for y in glob(os.path.join(x[0], '*.csv'))]
    for csvfile in allcsvs:
        try:
            df = pd.DataFrame()
            df = pd.read_csv(csvfile, header = None, index_col = False, skiprows = 1, usecols = [1, 2, 3, 4, 7, 12, 13, 14,15 ])
            df.columns = ['instID', 'datetime','price', 'openInterest', 'volume', 'bidPrice1', 'askPrice1', 'bidVol1', 'askVol1']
            df['datetime'] = pd.to_datetime(df.datetime)
            df['date'] = df.datetime.apply(lambda x:x.date())
            df['hour'] = df.datetime.apply(lambda x:x.hour)
            df['min'] = df.datetime.apply(lambda x:x.minute)
            df['sec'] = df.datetime.apply(lambda x:x.second)
            df['msec'] = df.datetime.apply(lambda x:x.microsecond)/1000
            df['tick_id'] = ((df['hour'] + 6) % 24)*100000 + df['min']*1000 + df['sec']*10 + df['msec']/100
            del df['datetime']
            print csvfile, len(df)
            df.to_sql(name = db_table, flavor = 'mysql', con = cnx, if_exists='append')
            cnx.commit()
        except:
            continue
    cnx.close()
    return 0

def load_hist_csv2sql(folder, db_table):
    dbconfig = {'user': 'harvey', 'password':'9619252y', 'host':'localhost', 'database': 'hist_data'}
    cnx = mysqlconn.connect(**dbconfig)
    cursor = cnx.cursor()
    allcsvs = [y for x in os.walk(folder) for y in glob(os.path.join(x[0], '*.csv'))]
    skipped_files = []
    for csvfile in allcsvs:
        try:
            str_list = csvfile.split('\\')
            filestr = str_list[-1].split('.')[0]
            fileinfo = filestr.split('_')
            trading_day = fileinfo[1]
            inst_str = fileinfo[0]
            if len(inst_str) <=4:
                print "skip %s" % csvfile
                continue
            if inst_str[-4:].isdigit():
                if int(inst_str[-4:]) < 5:
                    print "skip %s" % csvfile
                    continue
            filename = '\\\\'.join(csvfile.split('\\'))
            stmt = "load data local infile '" + filename + "' replace into table " + db_table
            stmt += " character set gb2312 fields terminated by ',' ignore 1 lines "
            stmt += "(@dummy, instID,  ts_str, price, openInterest, deltaOI, @dummy, "
            stmt += "dvol, dvol_open, dvol_close, @dummy, @dummy, "
            stmt += "bidPrice1, askPrice1, bidVol1, askVol1) "
            stmt += "set dtime = str_to_date(ts_str, '%Y-%m-%d %H:%i:%s.%f'), date = '{tdate}', ".format(tdate = trading_day)
            stmt += "hour=hour(dtime), min=minute(dtime), sec=second(dtime), msec=floor(microsecond(dtime)/1000),"
            stmt += "tick_id=mod(hour+6,24)*100000+min*1000+sec*10+floor(msec/100);"
            print csvfile
            cursor.execute(stmt)
            cnx.commit()
        except:
            print 'skip %s' % csvfile
            skipped_files.append(csvfile)
            continue
    cnx.close()
    print skipped_files
    return

def tick2ohlc(df):
    return pd.Series([df['dtime'][0], df['price'][0], df['price'].max(), df['price'].min(), df['price'][-1], df['dvol'].sum(), df['openInterest'][-1]],
                  index = ['datetime', 'open','high','low','close','volume', 'openInterest'])

def conv_tick2min(df):
    mdf = df.groupby([df['date'], df['hour'], df['min']]).apply(tick2ohlc).reset_index().set_index('datetime')
    return mdf

def conv_ohlc_freq(df, freq):
    highcol = pd.DataFrame(df['price']).resample(freq, how ='max').dropna()
    lowcol  = pd.DataFrame(df['price']).resample(freq, how ='min').dropna()
    opencol = pd.DataFrame(df['price']).resample(freq, how ='first').dropna()
    closecol= pd.DataFrame(df['price']).resample(freq, how ='last').dropna()
    volcol  = pd.DataFrame(df['dvol']).resample(freq, how ='sum').dropna()
    datecol  = pd.DataFrame(df['date']).resample(freq, how ='last').dropna()
    oicol  = pd.DataFrame(df['openInterest']).resample(freq, how ='last').dropna()
    res =  pd.concat([opencol, highcol, lowcol, closecol, volcol, oicol, datecol], join='outer', axis =1)
    res.columns = ['open', 'high', 'low', 'close', 'volume', 'openInterest', 'date' ]
    return res

def load_hist_tick(db_table, instID, sdate, edate):
    dbconfig = {'user': 'harvey', 'password':'9619252y', 'host':'localhost', 'database': 'hist_data'}
    stmt = "select instID, dtime, date, hour, min, sec, msec, price, dvol, openInterest from {dbtable} where instID='{inst}' ".format(dbtable=db_table, inst=instID)
    stmt += "and date >= '%s' " % sdate.strftime('%Y-%m-%d')
    stmt += "and date <= '%s' " % edate.strftime('%Y-%m-%d')
    stmt += "order by dtime;"
    cnx = mysqlconn.connect(**dbconfig)
    df = pd.io.sql.read_sql(stmt, cnx, index_col = 'dtime')
    return df

def load_hist_min(db_table, instID):
    dbconfig = {'user': 'harvey', 'password':'9619252y', 'host':'localhost', 'database': 'hist_data'}
    stmt = "select instID, exch, dtime, date, min_id, open, high, low, close, volume, openInterest from {dbtable} where instID='{inst}' ".format(dbtable=db_table, inst=instID)
    stmt += "order by dtime;"
    cnx = mysqlconn.connect(**dbconfig)
    df = pd.io.sql.read_sql(stmt, cnx, index_col = 'dtime')
    return df

def conv_db_htick2min(db_table, inst_file, out_table = 'hist_fut_min', database = 'hist_data', dstep = 10):
    conf_dict = {}
    instIDs = []
    if inst_file == '':
        instIDs =  get_col_dist_values(database + '.' + db_table, 'instID',{})
        conf_dict = {'instIDs': instIDs}
        try:
            inst_file = 'instID_file.json'
            with open(inst_file, 'w') as ofile:
                json.dump(conf_dict, ofile)
        except:
            pass
    else:
        with open(inst_file, 'r') as infile:
            conf_dict = json.load(infile)
        instIDs = conf_dict['instIDs']
    dbconfig = {'user': 'harvey', 'password':'9619252y', 'host':'localhost', 'database': database}
    cnx = mysqlconn.connect(**dbconfig)
    for inst in instIDs:
        field_dict = {'instID': "\'"+inst+"\'"}
        datestr_list = get_col_dist_values(database + '.' + db_table, 'date', field_dict)
        mdata = pd.DataFrame()
        prod = misc.inst2product(inst)
        exch = misc.inst2exch(inst)
        num_run = (len(datestr_list)+dstep-1)/dstep
        for idx in range(num_run):
            s_idx = idx * dstep
            e_idx = min((idx + 1) *dstep - 1, len(datestr_list)-1)
            sdate = datetime.datetime.strptime(datestr_list[s_idx], "%Y-%m-%d").date()
            edate = datetime.datetime.strptime(datestr_list[e_idx], "%Y-%m-%d").date()
            df = load_hist_tick(db_table, inst, sdate, edate)
            mdf = conv_ohlc_freq(df, '1Min')
            mdf['min_id'] =  ((mdf.index.hour + 6) % 24) * 100 + mdf.index.minute
            mdf = backtest.cleanup_mindata(mdf, prod)
            mdf.index.name = 'datetime'
            mdf['instID'] = inst
            mdf['exch'] = exch
            mdf = mdf.reset_index()
            mdf.set_index(['instID', 'exch', 'datetime'], inplace = True)
            mdf.to_sql(name = out_table, flavor = 'mysql', con = cnx, if_exists='append')
            cnx.commit()
            print inst, sdate, edate, len(mdf)
    cnx.close()
    return

def conv_db_htmin2daily(db_table, inst_file, out_table = 'hist_fut_daily', database = 'hist_data'):
    conf_dict = {}
    instIDs = []
    if inst_file == '':
        instIDs =  get_col_dist_values(database + '.' + db_table, 'instID',{})
        conf_dict = {'instIDs': instIDs}
        try:
            inst_file = 'instID_file.json'
            with open(inst_file, 'w') as ofile:
                json.dump(conf_dict, ofile)
        except:
            pass
    else:
        with open(inst_file, 'r') as infile:
            conf_dict = json.load(infile)
        instIDs = conf_dict['instIDs']
    dbconfig = {'user': 'harvey', 'password':'9619252y', 'host':'localhost', 'database': database}
    cnx = mysqlconn.connect(**dbconfig)
    for inst in instIDs:
        df = load_hist_min(db_table, inst)
    cnx.close()
    return

def get_col_dist_values(db_table, col_name, field_dict):
    dbconfig = {'user': 'harvey', 'password':'9619252y', 'host':'localhost'}
    stmt = 'select distinct({colname}) from {dbtable}'.format(colname = col_name, dbtable = db_table )
    nlen = len(field_dict.values())
    if nlen > 0:
        stmt += ' where'
        for idx, field in enumerate(field_dict.keys()):
            stmt += " {fieldname}={fvalue}".format(fieldname = field, fvalue = field_dict[field])
            if idx < nlen - 1:
                stmt += " and"
    stmt += ";"
    print stmt
    cnx = mysqlconn.connect(**dbconfig)
    cursor = cnx.cursor()
    cursor.execute(stmt)
    #cnx.commit()
    keys = []
    for line in cursor:
        keys.append(str(line[0]))
    cnx.close()
    return keys

if __name__ == '__main__':
    print
