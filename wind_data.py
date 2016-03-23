import datetime
import csv
import os.path
import mysql.connector
import math
import pandas as pd
from WindPy import w
w.start()
dbconfig = {'user': 'harvey', 
          'password':'9619252y', 
          'host':'localhost',
          'database': 'blueshale',
          }

product_code = {'CFE':['IF','TF'],
                'SHF':['cu','al','zn','pb','rb','ru','bu','hc','ag','au'], 
                'DCE': ['c', 'j', 'jd', 'a', 'm', 'y', 'p', 'l', 'v', 'jm', 'i', 'fb', 'bb', 'pp','cs'],
                'CZC': ['WH','CF', 'SR', 'TA', 'OI', 'ME', 'FG', 'RS', 'RM', 'TC', 'PM', 'RI', 'JR', 'LR', 'SM', 'SF'],
                'SH':  ['510050', '510330', '510300', '510180'],
                'SZ':  ['159901', '159912', '159919'] }

contMonth = {'IF':range(1,13),
            'TF': range(1,13),
            'cu':range(1,13),
            'al':range(1,13),
            'zn':range(1,13),
            'pb':range(1,13),
            'ru':[1,5,9],
            'au':[6,12],
            'ag':[6,12],
            'rb':[1,5,10],
            'bu':[1,5,9],
            'hc':[1,5,9],
            'c':[1,5,9],
            'a':[1,5,9],
            'm':[1,5,9],
            'y':[1,5,9],
            'p':[1,5,9],
            'l':[1,5,9],
            'v':[1,5,9],
            'j':[1,5,9],
            'jm':[1,5,9],
            'i':[1,5,9],
            'jd':[1,5,9],
            'fb':[1,5,9],
            'bb':[1,5,9],
            'pp':[1,5,9],
            'WH':[1,5,9],
            'CF':[1,5,9],
            'SR':[1,5,9],
            'OI':[1,5,9],
            'TA':[1,5,9],
            'TC':[1,5,9],
            'ME':[1,5,9],
            'FG':[1,5,9],
            'RS':[1,5,9],
            'RM':[1,5,9],
            'PM':[1,5,9],
            'RI':[1,5,9], 
            'JR':[1,5,9], 
            'LR':[1,5,9],     
            'SM':[1,5,9],
            'SF':[1,5,9],
            'cs':[1,5,9]}      
            
def get_min_id(dt):
    return math.ceil((((dt.hour+6)%24)*100000+dt.minute*1000+dt.second*10+dt.microsecond/100000)/1000)

def get_hist_cont(endD,contStartFile, outFile):
    reader=csv.reader(file(contStartFile,'rb'))
    conts = []
    for line in reader:
        product = line[0]
        startD = datetime.datetime.strptime(line[1], "%Y/%m/%d").date()
        st_year  = startD.year
        
        for yr in range(st_year, endD.year+1):
            for mth in range(1,13):
                if (mth in contMonth[product]):
                    curr_mth = datetime.date(yr,mth,1)
                    if (curr_mth > startD) and (curr_mth <= endD):
                        if product in product_code['CZC']:
                            contLabel = product + "%01d" %(yr%10) + "%02d" % mth
                        else:
                            contLabel = product + "%02d" %(yr%100) + "%02d" % mth
                        conts.append(contLabel)
    
    out = {'contract': conts }
    dump2csvfile(out,outFile)
    return True
    
def import_csv_data(filename):
    reader = csv.reader(file(filename, 'rb'))
    contList = []
    datapath = 'C:\\dev\\src\\ktlib\\data2\\'
    
    for line in reader:
        contList.append(line[0])

    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()

    for cont in contList:
        
        if cont[1].isalpha(): key = cont[:2]
        elif cont[0].isalpha(): key = cont[:1]
        else: key = cont

        ex = 'SH'
        for exch in product_code.keys():
            if key in product_code[exch]:
                ex = exch
        
        if ex == 'SHF':
            ex = 'SHFE'
        elif ex == 'CZC':
            ex = 'CZCE'
        elif ex == 'CFE':
            ex = 'CFFEX'
        minfile = datapath + cont + '_min.csv'
        if os.path.isfile(minfile):
            dbtable = 'fut_min'
            data_reader = csv.reader(file(minfile, 'rb'))
            fields = ['instID', 'exch', 'datetime', 'min_id', 'open', 'close', 'high', 'low', 'volume', 'openInterest']
            data = []
            for idx, line in enumerate(data_reader):
                if idx > 0:
                    if 'nan' in [line[0],line[2],line[3],line[4], line[6]]: continue
                    vol   = int(float(line[0]))
                    if vol <= 0: continue
                    dtime = datetime.datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S.%f')
                    dtime_str = dtime.strftime('%Y-%m-%d %H:%M:%S')
                    high  = float(line[2])
                    low   = float(line[3])
                    close = float(line[4])
                    if line[5] == 'nan':
                        oi = 0
                    else:
                        oi = int(float(line[5]))
                    open  = float(line[6])
                    min_id = get_min_id(dtime)
                    data.append((cont, ex, dtime_str, min_id, open, close, high, low, vol, oi))
            
            if len(data)>0:
                print "inserting minute data for contract %s with total rows %s" % (cont, len(data))
                stmt = "REPLACE INTO {table} ({variables}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(table=dbtable,variables=','.join(fields))   
                cursor.executemany(stmt, data)
                cnx.commit()
            else:
                print "no minute data for contract %s" % (cont)
        else:
            print "no minute csv file for contract %s" % (cont)
            
        dayfile = datapath + cont + '_daily.csv'
        if os.path.isfile(dayfile):
            dbtable = 'fut_daily'
            data_reader = csv.reader(file(dayfile, 'rb'))
            fields = ['instID', 'exch', 'date', 'open', 'close', 'high', 'low', 'volume', 'openInterest']
            data = []
            for idx, line in enumerate(data_reader):
                if idx > 0 :
                    if 'nan' in [line[0],line[2],line[3],line[4], line[6]]: continue
                    vol   = int(float(line[0]))
                    if vol <= 0: continue
                    dtime = datetime.datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S.%f')
                    dtime_str = dtime.strftime('%Y-%m-%d')
                    high  = float(line[2])
                    low   = float(line[3])
                    close = float(line[4])
                    if line[5] == 'nan':
                        oi = 0
                    else:
                        oi = int(float(line[5]))
                    open  = float(line[6])
                    data.append((cont, ex, dtime_str, open, close, high, low, vol, oi))
            
            if len(data)>0:
                print "inserting daily data for contract %s with total rows %s" % (cont, len(data))
                stmt = "REPLACE INTO {table} ({variables}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(table=dbtable,variables=','.join(fields))   
                cursor.executemany(stmt, data)
                cnx.commit()
            else:
                print "no daily data for contract %s" % (cont)
        else:
            print "no daily csv file for contract %s" % (cont)
                                
    cursor.close()
    cnx.close()
    return True

def load_live_cont(d_start, d_end):
    cnx = mysql.connector.connect(**dbconfig)
    end_adj = d_end + datetime.timedelta(days=1)
    stmt = "select instID, start_date, expiry from contract_list where "
    stmt = stmt + "expiry >= '%s' " % d_start.strftime('%Y-%m-%d')
    stmt = stmt + "and start_date <= '%s' " % end_adj.strftime('%Y-%m-%d')
    df = pd.io.sql.read_sql(stmt, cnx, index_col = 'instID')
    cnx.close()
    return df
    
def get_min_data(filename):
    file_folder = 'C:\\dev\\src\\ktlib\\data3\\'
    reader = csv.reader(file(filename, 'rb'))
    contList = []
    fields = 'open,close,high,low,volume,oi'
    contStart = []
    contEnd = []
    for line in reader:
        contList.append(line[0])
        contStart.append(line[1])
        contEnd.append(line[2])
    
    #w.start()
    for cont, startD, endD in zip(contList, contStart, contEnd):
        if cont[1].isalpha(): key = cont[:2]
        else: key = cont[:1]
        ex = 'SH'
        for exch in product_code.keys():
            if key in product_code[exch]:
                ex = exch
                
        ticker = cont + '.' + ex
        startmin = ""
        endMin = ""
        
        if ex == 'CFE':
            startMin = " 09:14:00"
            endMin = " 15:15:00"
        else:
            startMin = " 08:59:00"
            endMin = " 15:00:00"
            
        if ex == 'CFE':
            startMin = " 09:14:00"
            endMin = " 15:15:00"
        else:
            startMin = " 08:59:00"
            endMin = " 15:00:00"
            
        try:
            sdate = datetime.datetime.strptime(startD, "%Y/%m/%d")
            edate = datetime.datetime.strptime(endD, "%Y/%m/%d")
            sMin = datetime.datetime.strptime(startD + startMin, "%Y/%m/%d %H:%M:%S")
            eMin = datetime.datetime.strptime(endD + endMin, "%Y/%m/%d %H:%M:%S")
            print ticker, sMin, eMin
            if edate > datetime.date(2009,1,1):
                raw_data = w.wsi(ticker,fields,sMin,eMin)
                if len(raw_data.Data)>1:
                    outfile = file_folder + cont+'_min.csv'
                    output={'datetime':raw_data.Times, 
                        'open':raw_data.Data[0],
                        'close':raw_data.Data[1],
                        'high':raw_data.Data[2],
                        'low':raw_data.Data[3],
                        'volume':raw_data.Data[4],
                        'openInterest':raw_data.Data[5]}
                    dump2csvfile(output,outfile)
                else:
                    print "no min data obtained for ticker=%s" % ticker
            
            raw_data = w.wsd(ticker,fields,sdate,edate)
            if len(raw_data.Data)>1:
                outfile = file_folder + cont+'_daily.csv'
                output={'datetime':raw_data.Times, 
                        'open':raw_data.Data[0],
                        'close':raw_data.Data[1],
                        'high':raw_data.Data[2],
                        'low':raw_data.Data[3],
                        'volume':raw_data.Data[4],
                        'openInterest':raw_data.Data[5]}
                dump2csvfile(output,outfile)
            else:
                print "no daily data obtained for ticker=%s" % ticker
        except ValueError:
            pass

    w.stop()
    return True

def import_data_from_wind(d_start, d_end, file_folder='C:\\dev\\src\\ktlib\\data3\\', freq='d', contracts=[]):
    df = load_live_cont(d_start, d_end)
    contList = [str(inst) for inst in df.index]
    startDates = df.start_date
    endDates = df.expiry
    fields = 'open,close,high,low,volume,oi'
    if len(contracts) !=0:
        contList = contracts
    #w.start()
    for cont in contList:
        if cont[1].isalpha(): key = cont[:2]
        else: key = cont[:1]
        ex = 'SH'
        for exch in product_code.keys():
            if key in product_code[exch]:
                ex = exch
        ticker = cont + '.' + ex
        mth = int(cont[-2:])
        if (key not in contMonth):
            continue
        if mth not in contMonth[key]:
            continue
        start_d = max(d_start, startDates.ix[cont])
        end_d = min(d_end, endDates.ix[cont])
        try:
            if freq == 'm':
                print "loading min data for ticker = %s" % ticker
                raw_data = w.wsi(ticker,fields,start_d,end_d)
                if len(raw_data.Data)>1:
                    outfile = file_folder + cont+'_min.csv'
                    output={'datetime':raw_data.Times, 
                        'open':raw_data.Data[2],
                        'close':raw_data.Data[3],
                        'high':raw_data.Data[4],
                        'low':raw_data.Data[5],
                        'volume':raw_data.Data[6],
                        'openInterest':raw_data.Data[7]}
                    dump2csvfile(output,outfile)
                else:
                    print "no min data obtained for ticker=%s" % ticker
            else:
                print "loading daily data for ticker = %s" % ticker
                raw_data = w.wsd(ticker,fields,start_d,end_d)
                if len(raw_data.Data)>1:
                    outfile = file_folder + cont+'_daily.csv'
                    output={'datetime':raw_data.Times, 
                            'open':raw_data.Data[0],
                            'close':raw_data.Data[1],
                            'high':raw_data.Data[2],
                            'low':raw_data.Data[3],
                            'volume':raw_data.Data[4],
                            'openInterest':raw_data.Data[5]}
                    dump2csvfile(output,outfile)
                else:
                    print "no daily data obtained for ticker=%s" % ticker
        except ValueError:
            pass

    w.stop()
    return True

def load_csv_to_db(d_start, d_end, datapath='C:\\dev\\src\\ktlib\\data3\\'):
    df = load_live_cont(d_start, d_end)
    contList = [str(inst) for inst in df.index]
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()
    for cont in contList:
        if cont[1].isalpha(): key = cont[:2]
        elif cont[0].isalpha(): key = cont[:1]
        else: key = cont
        ex = 'SH'
        for exch in product_code.keys():
            if key in product_code[exch]:
                ex = exch
        if ex == 'SHF':
            ex = 'SHFE'
        elif ex == 'CZC':
            ex = 'CZCE'
        elif ex == 'CFE':
            ex = 'CFFEX'
            
        mth = int(cont[-2:])
        if (key not in contMonth):
            continue
        if mth not in contMonth[key]:
            continue
        minfile = datapath + cont + '_min.csv'
        if os.path.isfile(minfile):
            dbtable = 'fut_min'
            data_reader = csv.reader(file(minfile, 'rb'))
            fields = ['instID', 'exch', 'datetime', 'min_id', 'open', 'close', 'high', 'low', 'volume', 'openInterest']
            data = []
            for idx, line in enumerate(data_reader):
                if idx > 0:
                    if 'nan' in [line[0],line[2],line[3],line[4], line[6]]: continue
                    vol   = int(float(line[0]))
                    if vol <= 0: continue
                    dtime = datetime.datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S.%f')
                    dtime_str = dtime.strftime('%Y-%m-%d %H:%M:%S')
                    high  = float(line[2])
                    low   = float(line[3])
                    close = float(line[4])
                    if line[5] == 'nan':
                        oi = 0
                    else:
                        oi = int(float(line[5]))
                    open  = float(line[6])
                    min_id = get_min_id(dtime)
                    data.append((cont, ex, dtime_str, min_id, open, close, high, low, vol, oi))
            
            if len(data)>0:
                print "inserting minute data for contract %s with total rows %s" % (cont, len(data))
                stmt = "REPLACE INTO {table} ({variables}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(table=dbtable,variables=','.join(fields))   
                cursor.executemany(stmt, data)
                cnx.commit()
            else:
                print "no minute data for contract %s" % (cont)
        else:
            print "no minute csv file for contract %s" % (cont)
            
        dayfile = datapath + cont + '_daily.csv'
        if os.path.isfile(dayfile):
            dbtable = 'fut_daily'
            data_reader = csv.reader(file(dayfile, 'rb'))
            fields = ['instID', 'exch', 'date', 'open', 'close', 'high', 'low', 'volume', 'openInterest']
            data = []
            for idx, line in enumerate(data_reader):
                if idx > 0 :
                    if 'nan' in [line[0],line[2],line[3],line[4], line[6]]: continue
                    vol   = int(float(line[0]))
                    if vol <= 0: continue
                    dtime = datetime.datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S.%f')
                    dtime_str = dtime.strftime('%Y-%m-%d')
                    high  = float(line[2])
                    low   = float(line[3])
                    close = float(line[4])
                    if line[5] == 'nan':
                        oi = 0
                    else:
                        oi = int(float(line[5]))
                    open  = float(line[6])
                    data.append((cont, ex, dtime_str, open, close, high, low, vol, oi))
            
            if len(data)>0:
                print "inserting daily data for contract %s with total rows %s" % (cont, len(data))
                stmt = "REPLACE INTO {table} ({variables}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(table=dbtable,variables=','.join(fields))   
                cursor.executemany(stmt, data)
                cnx.commit()
            else:
                print "no daily data for contract %s" % (cont)
        else:
            print "no daily csv file for contract %s" % (cont)
                                
    cursor.close()
    cnx.close()
    return True

def dump2csvfile(data, outfile):
    output = [];    
    for key in data.keys():
        x = [key] + data[key];
        output.append(x);
             
    item_len = len(output[0]);    
    with open(outfile,'wb') as test_file:
        file_writer = csv.writer(test_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL);
        for i in range(item_len):
            file_writer.writerow([x[i] for x in output])
    return 0 

if __name__=="__main__":
    file_folder='C:\\dev\\src\\ktlib\\data3\\'
    d_start = datetime.date(2014,12,19)
    d_end = datetime.date(2014,12,29)
    import_data_from_wind(d_start, d_end, file_folder,'m')