import misc
import data_handler as dh
import pandas as pd
import numpy as np
import strategy as strat
import datetime
import openpyxl
import os
import backtest

def dual_thrust_sim( asset, start_date, end_date, nearby=1, rollrule='-20b', k = (1.0,1.0), marginrate = (0.05,0.05) ):
    ddf = misc.nearby(asset, nearby, start_date, end_date, rollrule, need_shift=True)
    mdf = misc.nearby(asset, nearby, start_date, end_date, rollrule, need_shift=True)
    res[cont] = {}
    ddf['TR'] = pd.concat([ddf['high']-ddf['close'], ddf['close']-ddf['low']], join='outer', axis=1).max(axis=1).shift(1) 
    ll = mdf.shape[0]
    mdf['pos'] = pd.Series([0]*ll, index = mdf.index)
    curr_pos = []
    closed_trades = []
	start_d = ddf.index[0]
	prev_d = start_d - datetime.timedelta(days=1)
    tradeid = 0
    for idx, dd in enumerate(mdf.index):
        mslice = mdf.ix[dd]
        d = dd.date()
        dslice = ddf.ix[d]
        if d < start_d + datetime.timedelta(days=1):
            continue
		d_open = dslice.open
		if (d.open == 0):
			if (prev_d < d):
				d_open = mslice.open
		else:
			d_open = dslice.open
		prev_d = d
		buytrig  = dslice.open + dslice.TR * k[0]
		selltrig = dslice.open - dslice.TR * k[1]
        if len(curr_pos) == 0:
            pos = 0
        else:
            pos = curr_pos[0].pos
		if (mslice.close >= buytrig) and (pos <=0 ):
            if len(curr_pos) > 0:
                curr_pos[0].close(mslice.close, dd)
                tradeid += 1
                curr_pos[0].set_tradeid(tradeid, -pos)
                closed_trade.append(curr_pos[0])
                curr_pos = []
            new_pos = strat.TradePos([mslice.contract], [1], 1, buytrig, 0)
            tradeid += 1
            new_pos.set_tradeid(tradeid, 1)
            new_pos.open(mslice.close, dd)
            curr_pos.append(new_pos)
            pos = 1
        elif (mslice.close <= selltrig) and (pos >=0 ):
            if len(curr_pos) > 0:
                curr_pos[0].close(mslice.close, dd)
                tradeid += 1
                curr_pos[0].set_tradeid(tradeid, -pos)
                closed_trade.append(curr_pos[0])
                curr_pos = []
            new_pos = strat.TradePos([mslice.contract], [1], -1, buytrig, 0)
            tradeid += 1
            new_pos.set_tradeid(tradeid, -1)
            new_pos.open(mslice.close, dd)
            curr_pos.append(new_pos)
            pos = -1
        mdf.ix[dd, 'pos'] = pos
    (res, pnl_ts) = backtest.get_pnl_stats( mdf, start_capital, 'm', )
    all_trades = {}
    for i, tradepos in enumerate(closed_trades):
        all_trades[ntrades+i] = strat.tradepos2dict(tradepos)
    results = pd.DataFrame.from_dict(res)
    trades = pd.DataFrame.from_dict(all_trades).T    
    return (results, trades)

def save_sim_results(file_prefix, res, trades):
    for pc in res:
        df = res[pc]
        fname = file_prefix+'_'+ pc +'_stats.csv'
        df.to_csv(fname)
        df = trades[pc]
        fname = file_prefix+'_'+ pc +'_trades.csv'
        df.to_csv(fname)
    return
    
if __name__=="__main__":
    rollrule = '-30b'
    commod_list1= ['m','y','a','p','v','l','ru','rb','au','cu','al','zn','ag','i','j','jm'] #
    start_dates1 = [datetime.date(2010,9,1)] * 9 + [datetime.date(2010,10,1)] * 3 + \
                [datetime.date(2012,7,1), datetime.date(2014,1,2), datetime.date(2011,6,1),datetime.date(2013,5,1)]
    commod_list2 = ['ME', 'CF', 'TA', 'PM', 'RM', 'SR', 'FG', 'OI', 'RI', 'TC', 'WH']
    start_dates2 = [datetime.date(2012, 2,1)] + [ datetime.date(2012, 6, 1)] * 2 + [datetime.date(2012, 10, 1)] + \
                [datetime.date(2013, 2, 1)] * 3 + [datetime.date(2013,6,1)] * 2 + [datetime.date(2013, 10, 1), datetime.date(2014,2,1)]
    commod_list = commod_list1+commod_list2
    start_dates = start_dates1 + start_dates2
    end_date = datetime.date(2014,11,7)
    systems = [[20,10],[15,7],[40,20],[55,20]]
    for sys in systems:
        file_prefix = 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\results\\turtle_R20b_%s' % sys[0]
        for cmd,sdate in zip(commod_list, start_dates):
            nearby = 1
            if cmd in ['cu','al','zn']:
                nearby = 2
                continue
            (res, trades) = turtle_sim( [cmd], sdate, end_date, nearby = nearby, rollrule = rollrule, signals = sys )
            print 'saving results for cmd = %s, sys= %s' % (cmd, sys[0])
            save_sim_results(file_prefix, res, trades)
            
            
