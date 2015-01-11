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
                
def fix_daily_by_tick(contlist, sdate, edate, is_forced=False):
    res = {}
    for inst in contlist:
        product = misc.inst2product(inst)
        if product in ['IF','TF']:
            continue        
        ddf = mysqlaccess.load_daily_data_to_df('fut_daily', inst, sdate, edate)
        tdf = mysqlaccess.load_tick_to_df('fut_tick', inst, sdate, edate, start_tick=300000, end_tick = 2100000)
        for d in list(set(tdf.date)):
            if (is_forced) or (d not in ddf.index) or (ddf.ix(d, 'open')==0):
                df = tdf[tdf['date']==d].sort(['tick_id'])
                ddata = {}
                ddata['date'] = d
                ddata['open'] = float(df.iloc[0].price)
                ddata['close'] = float(df.iloc[-1].price)
                ddata['high'] = float(df.iloc[-1].high)
                ddata['low'] = float(df.iloc[-1].low)
                ddata['volume'] = int(df.iloc[-1].volume)
                ddata['openInterest'] = int(df.iloc[-1].openInterest)
                print inst, ddata
                res[(inst,d)] = ddata
                mysqlaccess.insert_daily_data(inst, ddata, is_forced)
    return res

        
