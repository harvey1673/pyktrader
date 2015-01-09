'''
Created on Jun 07, 2014

@author: Harvey
'''

import datetime
import numpy
import mysql.connector
import csv
import os.path
import misc
import pandas as pd

dbconfig = {'user': 'harvey', 
          'password':'9619252y', 
          'host':'localhost',
          'database': 'blueshale',
          }
tick_columns = ['instID', 'date','hour','min','sec','msec','openInterest','volume','price','high','low','bidPrice1', 'bidVol1','askPrice1','askVol1']
min_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'openInterest', 'min_id']
daily_columns = [ 'date', 'open', 'high', 'low', 'close', 'volume', 'openInterest']

def insert_tick_data(inst, tick):
    if inst.isdigit():
        dbtable = 'stock_tick'
    else:
        dbtable = 'fut_tick'
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()
    col_list = tick.__dict__.keys()
    if 'timestamp' in col_list:
        col_list.remove('timestamp')
        
    stmt = "INSERT IGNORE INTO {table} ({variables}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(table=dbtable,variables=','.join(col_list))
    args = tuple([getattr(tick,col) for col in col_list])
    cursor.execute(stmt, args)
    cnx.commit()
    cnx.close()
    pass
    
def bulkinsert_tick_data(inst, ticks):
    if inst.isdigit():
        dbtable = 'stock_tick'
    else:
        dbtable = 'fut_tick'
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()
    col_list = ticks[0].__dict__.keys()
    if 'timestamp' in col_list:
        col_list.remove('timestamp')

    stmt = "INSERT IGNORE INTO {table} ({variables}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(table=dbtable,variables=','.join(col_list))
    args = [tuple([getattr(tick,col) for col in col_list]) for tick in ticks]    
    cursor.executemany(stmt, args)
    cnx.commit()
    cnx.close()
    pass

def insert_min_data(inst, min_data):
    if inst.isdigit():
        dbtable = 'stock_min'
    else:
        dbtable = 'fut_min'    
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()
    col_list = min_data.keys()
    exch = misc.inst2exch(inst)    
    stmt = "INSERT IGNORE INTO {table} (instID,exch,{variables}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(table=dbtable,variables=','.join(col_list))
    args = tuple([inst, exch]+[min_data[col] for col in col_list])
    cursor.execute(stmt, args)
    cnx.commit()
    cnx.close()
    pass

def insert_daily_data(inst, daily_data, open_only = False):
    if inst.isdigit():
        dbtable = 'stock_daily'
    else:
        dbtable = 'fut_daily'
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()
    col_list = daily_data.keys()
    exch = misc.inst2exch(inst)
    if open_only:
        col_list = ['date', 'open']
        cmd = "INSERT IGNORE"
    else:
        col_list = daily_data.keys()
        cmd = "REPLACE"
    stmt = "{commd} INTO {table} (instID,exch,{variables}) VALUES (%s,%s,{formats})".format(commd=cmd, table=dbtable,variables=','.join(col_list), formats=','.join(['%s']*len(col_list)))
    args = tuple([inst, exch]+[daily_data[col] for col in col_list])
    cursor.execute(stmt, args)
    cnx.commit()
    cnx.close()
    pass

def import_tick_from_file(dbtable):
    inst_list = ['IF1406', 'IO1406-C-2300','IO1406-P-2300','IO1406-C-2250',
                'IO1406-P-2250','IO1406-C-2200','IO1406-P-2200','IO1406-C-2150',
                'IO1406-P-2150','IO1406-C-2100','IO1406-P-2100','IO1406-C-2050',
                'IO1406-P-2050','IO1406-C-2000','IO1406-P-2000','IO1407-C-2300',
                'IO1407-P-2300','IO1407-C-2250','IO1407-P-2250','IO1407-C-2200',
                'IO1407-P-2200','IO1407-C-2150','IO1407-P-2150','IO1407-C-2100',
                'IO1407-P-2100','IO1407-C-2050','IO1407-P-2050','IO1407-C-2000',
                'IO1407-P-2000','IF1406']
    date_list = ['20140603','20140604','20140605','20140606']
    main_path = 'C:/dev/src/ktlib/pythonctp/data/'
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()
    for inst in inst_list:
        for date in date_list:
            path = main_path + inst + '/' + date + '_tick.txt'
            if os.path.isfile(path):
                stmt= "load data infile '{path}' replace into table {table} fields terminated by ',' lines terminated by '\n' (instID, date, @var1, sec, msec, openInterest, volume, price, high, low, bidPrice1, bidVol1, askPrice1, askVol1) set hour=(@var1 div 100), min=(@var1 % 100)".format(path=path, table=dbtable)
                cursor.execute(stmt)
                cnx.commit()
    cnx.close()
    pass

def insert_cont_data(cont):
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()
    col_list = cont.keys()
    stmt = "REPLACE INTO {table} ({variables}) VALUES (%s,%s,%s,%s,%s,%s) ".format(table='contract_list',variables=','.join(col_list))
    args = tuple([cont[col] for col in col_list])
    #print stmt, args
    cursor.execute(stmt, args)
    cnx.commit()
    cnx.close()
    pass

def prod_main_cont_exch(prodcode):
    cnx = mysql.connector.connect(**misc.mysqlaccess.dbconfig)
    cursor = cnx.cursor()
    stmt = "select exchange, contract from trade_products where product_code='{prod}' ".format(prod=prodcode)
    cursor.execute(stmt)
    out = [(exchange, contract) for (exchange, contract) in cursor]
    exch = str(out[0][0])
    cont = str(out[0][1])
    cnx.close()  
    cont_mth = [misc.month_code_map[c] for c in cont]
    return cont_mth, exch
    
def load_product_info(prod):
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()
    stmt = "select exchange, lot_size, tick_size, start_min, end_min, broker_fee from trade_products where product_code='{product}' ".format(product = prod)    
    cursor.execute(stmt)
    out = {}
    for (exchange, lot_size, tick_size, start_min, end_min, broker_fee) in cursor:
        out = {'exch': str(exchange), 
               'lot_size': lot_size, 
               'tick_size': float(tick_size), 
               'start_min': start_min, 
               'end_min': end_min, 
               'broker_fee': float(broker_fee)
               }
    cnx.close()
    return out

def load_alive_cont(sdate):
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()
    stmt = "select instID, product_code from contract_list where expiry>=%s"
    args = tuple([sdate])    
    cursor.execute(stmt, args)
    cont = []
    pc = []
    for line in cursor:
        cont.append(str(line[0]))
        prod = str(line[1])
        if prod not in pc:
            pc.append(prod)
    cnx.close()
    return cont, pc

def load_inst_marginrate(instID):
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()
    stmt = "select margin_l, margin_s from contract_list where instID='{inst}' ".format(inst = instID)    
    cursor.execute(stmt)
    out = (0,0)
    for (margin_l, margin_s) in cursor:
        out = (float(margin_l), float(margin_s))
    cnx.close()
    return out
        
def load_min_data_to_df(dbtable, inst, d_start, d_end, minid_start=1500, minid_end = 2115):
    cnx = mysql.connector.connect(**dbconfig)
    end_adj = d_end + datetime.timedelta(days=1)
    stmt = "select {variables} from {table} where instID='{instID}' ".format(variables=','.join(min_columns), table= dbtable, instID = inst)
    stmt = stmt + "and min_id >= %s " % minid_start
    stmt = stmt + "and min_id <= %s " % minid_end
    stmt = stmt + "and datetime >= '%s' " % d_start.strftime('%Y-%m-%d')
    stmt = stmt + "and datetime < '%s' " % end_adj.strftime('%Y-%m-%d')
    stmt = stmt + "order by date(datetime), min_id" 
    df = pd.io.sql.read_sql(stmt, cnx, index_col = 'datetime')
    cnx.close()
    return df    

def load_daily_data_to_df(dbtable, inst, d_start, d_end):
    cnx = mysql.connector.connect(**dbconfig)
    stmt = "select {variables} from {table} where instID='{instID}' ".format(variables=','.join(daily_columns), table= dbtable, instID = inst)
    stmt = stmt + "and date >= '%s' " % d_start.strftime('%Y-%m-%d')
    stmt = stmt + "and date <= '%s' " % d_end.strftime('%Y-%m-%d')
    stmt = stmt + "order by date" 
    df = pd.io.sql.read_sql(stmt, cnx, index_col = 'date')
    cnx.close()
    return df

def load_tick_to_df(dbtable, inst, d_start, d_end, start_tick=1500000, end_tick = 2115000):
    tick_columns = ['instID', 'date','tick_id','hour','min','sec','msec','openInterest','volume','price','high','low','bidPrice1', 'bidVol1','askPrice1','askVol1']
    cnx = mysql.connector.connect(**dbconfig)
    stmt = "select {variables} from {table} where instID='{instID}' ".format(variables=','.join(tick_columns), table= dbtable, instID = inst)
    stmt = stmt + "and tick_id >= %s " % minid_start
    stmt = stmt + "and tick_id <= %s " % minid_end
    stmt = stmt + "and datetime >='%s' " % d_start.strftime('%Y-%m-%d')
    stmt = stmt + "and datetime <='%s' " % d_end.strftime('%Y-%m-%d')
    stmt = stmt + "order by date, tick_id" 
    df = pd.io.sql.read_sql(stmt, cnx)
    cnx.close()
    return df    

def load_tick_data(dbtable, insts, d_start, d_end):
    cnx = mysql.connector.connect(**dbconfig)
    cursor = cnx.cursor()
    stmt = "select {variables} from {table} where instID in ('{instIDs}') ".format(variables=','.join(tick_columns), table= dbtable, instIDs= "','".join(insts))
    stmt = stmt + "and date >= '%s' " % d_start.strftime('%Y-%m-%d')
    stmt = stmt + "and date <= '%s' " % d_end.strftime('%Y-%m-%d')
    stmt = stmt + "order by date, hour, min, sec, msec" 
    cursor.execute(stmt)
    all_ticks = []
    for line in cursor:
        tick = dict([(key,val) for (key, val) in zip(tick_columns, line)])
        tick['timestamp'] = datetime.datetime.combine(tick['date'], datetime.time(hour=tick['hour'], minute=tick['min'], second=tick['sec'], microsecond=tick['msec']*1000))
        all_ticks.append(tick)     
    cnx.close()
    return all_ticks
    
def insert_min_data_to_df(df, min_data):
    new_data = { key: min_data[key] for key in min_columns[1:] }
    df.loc[min_data['datetime']] = pd.Series(new_data)

def insert_daily_data_to_df(df, daily_data):
    new_data = {key: daily_data[key] for key in daily_columns[1:]}
    df.loc[daily_data['date']] = pd.Series(new_data)