import mysqlaccess
import misc
import data_handler

def filter_main_cont(sdate):
    insts, prods  = mysqlaccess.load_alive_cont(sdate)
    main_cont = {}
    for pc in prods:
        main_cont[pc], exch = mysqlaccess.prod_main_cont_exch(pc)
    main_insts = []
    for inst in insts:
        pc = misc.inst2product(inst)
        mth = int(inst[-2:])
        if mth in main_cont[pc]:
            main_insts.append(inst)
    return main_insts
    
def fix_daily_data(contlist, sdate, edate):
    for inst in contlist:
        ddf = mysqlaccess.load_daily_data_to_df('fut_daily', inst, sdate, edate)
        mdf = mysqlaccess.load_min_data_to_df('fut_min', inst, sdate, edate, minid_start=300, minid_end = 2115)
        dailydata = data_handler.conv_ohlc_freq(mdf, 'D')
        for dd in dailydata.index:
            d = dd.date()
            dslice = dailydata.ix[dd]
            if d not in ddf.index:
                ddata = {}
                ddata['date'] = d
                ddata['open'] = float(dslice.open)
                ddata['close'] = float(dslice.close)
                ddata['high'] = float(dslice.high)
                ddata['low'] = float(dslice.low)
                ddata['volume'] = int(dslice.volume)
                ddata['openInterest'] = int(dslice.openInterest)
                print inst, ddata
                mysqlaccess.insert_daily_data(inst, ddata)

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
                
def fix_daily_by_tick(contlist, sdate, edate, is_forced=False):
    for inst in contlist:
        product = inst2product(inst)
        prod_info = mysqlaccess.load_product_info(product)		
        ddf = mysqlaccess.load_daily_data_to_df('fut_daily', inst, sdate, edate)
        tdf = mysqlaccess.load_tick_to_df('fut_tick', inst, sdate, edate, start_tick=prod_info['start_min'] * 1000, end_tick = prod_info['start_min'] * 1000)
		for d in list(set(tdf.date)):
            if (is_forced) or (d not in ddf.index) or ddf.ix(d, 'open')==0):
				df = tdf[tdf['date']==d].sort(['tick_id'])
				ddata = {}
                ddata['date'] = d
                ddata['open'] = float(df.price[0])
                ddata['close'] = float(df.price[-1])
                ddata['high'] = float(df.high[-1])
                ddata['low'] = float(df.low[-1])
                ddata['volume'] = int(df.volume[-1])
                ddata['openInterest'] = int(df.openInterest[-1])
                print inst, ddata
                #mysqlaccess.insert_daily_data(inst, ddata)
				
def get_daily_by_tick(inst, cur_date, start_tick=1500000, end_tick=2100000):
	df = mysqlaccess.load_tick_to_df('fut_tick', inst, cur_date, cur_date, start_tick, end_tick)
	ddata = {}
	ddata['date'] = d
	ddata['open'] = float(df.price[0])
	ddata['close'] = float(df.price[-1])
	ddata['high'] = float(df.high[-1])
	ddata['low'] = float(df.low[-1])
	ddata['volume'] = int(df.volume[-1])
	ddata['openInterest'] = int(df.openInterest[-1])
	return ddata

        
