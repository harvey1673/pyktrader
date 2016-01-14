import data_saver
import tushare as ts
import datetime
import pandas as pd
import mysql.connector as mysqlconn
import misc
import os
import urllib2
import pytz
import patoolib
import mysqlaccess as db
from glob import glob

from bs4 import BeautifulSoup
from datetime import datetime
from pandas.io.data import DataReader

SITE = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
START = datetime(1900, 1, 1, 0, 0, 0, 0, pytz.utc)
END = datetime.today().utcnow()


def scrape_list(site):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(site, headers=hdr)
    page = urllib2.urlopen(req)
    soup = BeautifulSoup(page)

    table = soup.find('table', {'class': 'wikitable sortable'})
    sector_tickers = dict()
    for row in table.findAll('tr'):
        col = row.findAll('td')
        if len(col) > 0:
            sector = str(col[3].string.strip()).lower().replace(' ', '_')
            ticker = str(col[0].string.strip())
            if sector not in sector_tickers:
                sector_tickers[sector] = list()
            sector_tickers[sector].append(ticker)
    return sector_tickers


def download_ohlc(sector_tickers, start, end):
    sector_ohlc = {}
    for sector, tickers in sector_tickers.iteritems():
        print 'Downloading data from Yahoo for %s sector' % sector
        data = DataReader(tickers, 'yahoo', start, end)
        for item in ['Open', 'High', 'Low']:
            data[item] = data[item] * data['Adj Close'] / data['Close']
        data.rename(items={'Open': 'open', 'High': 'high', 'Low': 'low',
                           'Adj Close': 'close', 'Volume': 'volume'},
                    inplace=True)
        data.drop(['Close'], inplace=True)
        sector_ohlc[sector] = data
    print 'Finished downloading data'
    return sector_ohlc


def store_HDF5(sector_ohlc, path):
    with pd.get_store(path) as store:
        for sector, ohlc in sector_ohlc.iteritems():
            store[sector] = ohlc


def get_snp500():
    sector_tickers = scrape_list(SITE)
    sector_ohlc = download_ohlc(sector_tickers, START, END)
    store_HDF5(sector_ohlc, 'snp500.h5')

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
    cnx = mysqlconn.connect(**db.dbconfig)
    cursor = cnx.cursor()
    allcsvs = [y for x in os.walk(folder) for y in glob(os.path.join(x[0], '*.csv'))]
    for csvfile in allcsvs:
        try:
            stmt = "load data local infile '{file}' replace into table {dbtable} ".format(file=csvfile, dbtable=db_table)
            stmt += "fields terminated by ',' ignore 1 lines "
            stmt += "(@dummy, instID,  @datestr, price, openInterest, deltaOI, @dummy, "
            stmt += "dvol, dvol_open, dvol_close, @dummy, @dummy, "
            stmt += "bidPrice1, askPrice1, bidVol1, askVol1) "
            stmt += "set tstamp = str_to_date(@datestr, '%Y-%m-%d %H:%i:%s.%f');"
            print csvfile
            cursor.execute(stmt)
            cnx.commit()
        except:
            print 'skip %s' % csvfile
            continue
    cnx.close()
    return

if __name__ == '__main__':
    print
