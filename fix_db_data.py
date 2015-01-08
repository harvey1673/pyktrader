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
                
def fix_daily_by_tick(contlist, cur_date):
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
        