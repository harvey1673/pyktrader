import misc
import agent
import data_handler as dh
import pandas as pd
import numpy as np
import strategy as strat
import datetime
import backtest

def aberration( asset, start_date, end_date, freqs, windows, config):
    nearby  = config['nearby']
    rollrule = config['rollrule']
    file_prefix = config['file_prefix'] + '_' + asset + '_'
	df = misc.nearby(asset, nearby, start_date, end_date, rollrule, 'm', need_shift=True)
	
    output = {}
    for ix, freq in enumerate(freqs):
		xdf = dh.conv_ohlc_freq(df, freq):
        for iy, win in enumerate(windows):
            idx = ix*10+iy
            config['win'] = win
            (res, closed_trades, ts) = aberration_sim( xdf, mdf, , config)
            output[idx] = res
            print 'saving results for scen = %s' % str(idx)
            all_trades = {}
            for i, tradepos in enumerate(closed_trades):
                all_trades[i] = strat.tradepos2dict(tradepos)
            fname = file_prefix + str(idx) + '_trades.csv'
            trades = pd.DataFrame.from_dict(all_trades).T  
            trades.to_csv(fname)
            fname = file_prefix + str(idx) + '_dailydata.csv'
            ts.to_csv(fname)
    fname = file_prefix + 'stats.csv'
    res = pd.DataFrame.from_dict(output)
    res.to_csv(fname)
    return 

def aberration_sim( xdf, mdf, config):
    marginrate = config['marginrate']
    offset = config['offset']
	win = config['win']
    start_equity = config['capital']
    tcost = config['trans_cost']
	unit = config['unit']
    df['ma'] = dh.MA(df, win).shift(1)
	std = dh.STDDEV(df, win).shift(1)
	df['upbnd'] = df['ma'] + std
	df['lowbnd'] = df['ma'] - std
    ll = df.shape[0]
    df['pos'] = pd.Series([0]*ll, index = mdf.index)
    df['cost'] = pd.Series([0]*ll, index = mdf.index)
    curr_pos = []
    closed_trades = []
    start_d = df.index[0].date()
    end_d = df.index[-1].date()
    tradeid = 0
    for idx, dd in enumerate(df.index):
        mslice = df.ix[dd]
        min_id = agent.get_min_id(dd)
        d = dd.date()
        if len(curr_pos) == 0:
            pos = 0
        else:
            pos = curr_pos[0].pos
		df.ix[dd, 'pos'] = pos
        if np.isnan(mslice.ma):
            continue
		if (min_id >=2054):
			if (pos!=0) and (d == end_d):
				curr_pos[0].close(mslice.close - misc.sign(pos) * offset , dd)
                tradeid += 1
                curr_pos[0].exit_tradeid = tradeid
                closed_trades.append(curr_pos[0])
                curr_pos = []
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost) 
			continue
        else:
            if ((mslice.close >= mslice.ma) and (pos<0 )) or (mslice.close <= mslice.ma) and (pos>0 ) :
				curr_pos[0].close(mslice.close+offset, dd)
				tradeid += 1
				curr_pos[0].exit_tradeid = tradeid
				closed_trades.append(curr_pos[0])
				curr_pos = []
				mdf.ix[dd, 'cost'] -= abs(pos) * (offset + mslice.close*tcost)
				pos = 0
			pos = (mslice.close>=mslice.upbnd) * unit -(mslice.close<=mslice.lowbnd) * unit
			if abs(pos)>0:
				target = min(mslice.close>=mslice.upbnd) * mslice.upbnd +(mslice.close<=mslice.lowbnd) * mslice.lowbnd
                new_pos = strat.TradePos([mslice.contract], [1], pos, target, mslice.upbnd+mslice.lowbnd-target)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close + misc.sign(pos)*offset, dd)
                curr_pos.append(new_pos)
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
        mdf.ix[dd, 'pos'] = pos
            
    (res_pnl, ts) = backtest.get_pnl_stats( df, start_equity, marginrate, 'm')
    res_trade = backtest.get_trade_stats( closed_trades )
    res = dict( res_pnl.items() + res_trade.items())
    return (res, closed_trades, ts)
    
def run_sim(asset, start_date, end_date):
    config = {'nearby':1, 
              'rollrule':'-40b', 
              'marginrate':(0.05, 0.05), 
              'capital': 10000,
              'offset': 0,
              'trans_cost': 0.0,
			  'scaler': (2.0, 2.0),
              'unit': 1,
              'file_prefix': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\results\\Aberration_'}

    #commod_list1= ['m','y','a','p','v','l','ru','rb','au','cu','al','zn','ag','i','j','jm'] #
    #start_dates1 = [datetime.date(2010,9,1)] * 9 + [datetime.date(2010,10,1)] * 3 + \
    #            [datetime.date(2012,7,1), datetime.date(2014,1,2), datetime.date(2011,6,1),datetime.date(2013,5,1)]
    #commod_list2 = ['ME', 'CF', 'TA', 'PM', 'RM', 'SR', 'FG', 'OI', 'RI', 'TC', 'WH']
    #start_dates2 = [datetime.date(2012, 2,1)] + [ datetime.date(2012, 6, 1)] * 2 + [datetime.date(2012, 10, 1)] + \
    #            [datetime.date(2013, 2, 1)] * 3 + [datetime.date(2013,6,1)] * 2 + [datetime.date(2013, 10, 1), datetime.date(2014,2,1)]
    #commod_list = commod_list1+commod_list2
    #start_dates = start_dates1 + start_dates2
    #for asset, sdate in zip(commod_list, start_dates):

    if asset in ['cu', 'al', 'zn']:
        config['nearby'] = 3
        config['rollrule'] = '-1b'
    elif asset in ['IF']:
        config['rollrule'] = '-1b'
        
    freqs = ['5Min', '15Min', '30Min', '60Min', 'D']
    windows = [35]
    aberration( asset, start_date, end_date, freqs, windows, config)

if __name__=="__main__":
    args = sys.argv[1:]
    if len(args) < 3:
        end_d = datetime.date(2014,11,30)
    else:
        end_d = datetime.datetime.strptime(args[2], '%Y%m%d').date()
    if len(args) < 2:
        start_d = datetime.date(2014,1,2)
    else:
        start_d = datetime.datetime.strptime(args[1], '%Y%m%d').date()
    if len(args) < 1:
        asset = 'm'
    else:
        asset = args[0]
    run_sim(asset, start_d, end_d)

