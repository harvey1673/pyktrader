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
	freq = '5min'
    file_prefix = config['file_prefix'] + '_' + asset + '_'
    if 'min' in freq:
		df = misc.nearby(asset, nearby, start_date, end_date, rollrule, 'm', need_shift=True)
	else:
		df = misc.nearby(asset, nearby, start_date, end_date, rollrule, 'd', need_shift=True)
	
    output = {}
    for ix, freq in enumerate(freqs):
        ts_data = df['close'].resample(freq,  how ='last').dropna()
        for iy, win in enumerate(windows):
            idx = ix*10+iy
            config['k'] = k
            (res, closed_trades, ts) = aberration_sim( ts_data, config)
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

def aberration_sim( ddf, mdf, config):
    marginrate = config['marginrate']
    offset = config['offset']
	k = config['scaler']
    start_equity = config['capital']
    win = config['win']
    tcost = config['trans_cost']
    ddf['TR'] = pd.concat([pd.rolling_max(ddf.high, win) - pd.rolling_min(ddf.close, win), 
                           pd.rolling_max(ddf.close, win) - pd.rolling_min(ddf.low, win)], 
                           join='outer', axis=1).max(axis=1).shift(1) 
    ll = mdf.shape[0]
    mdf['pos'] = pd.Series([0]*ll, index = mdf.index)
    mdf['cost'] = pd.Series([0]*ll, index = mdf.index)
    curr_pos = []
    closed_trades = []
    start_d = ddf.index[0]
    end_d = ddf.index[-1]
    prev_d = start_d - datetime.timedelta(days=1)
    tradeid = 0
    for idx, dd in enumerate(mdf.index):
        mslice = mdf.ix[dd]
        min_id = agent.get_min_id(dd)
        d = dd.date()
        dslice = ddf.ix[d]
        if np.isnan(dslice.TR):
            continue
        d_open = dslice.open
        if (d_open == 0):
            if (prev_d < d):
                d_open = mslice.open
        else:
            d_open = dslice.open
        if (d_open <= 0):
            continue
        prev_d = d
        buytrig  = d_open + dslice.TR * k[0]
        selltrig = d_open - dslice.TR * k[1]
        if len(curr_pos) == 0:
            pos = 0
        else:
            pos = curr_pos[0].pos
        
        if (min_id >= 2055):
            if (pos != 0) and (close_daily or (d == end_d)):
                curr_pos[0].close(mslice.close - misc.sign(pos) * offset , dd)
                tradeid += 1
                curr_pos[0].exit_tradeid = tradeid
                closed_trades.append(curr_pos[0])
                curr_pos = []
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost) 
            continue
        else:
            if (mslice.close >= buytrig) and (pos <=0 ):
                if len(curr_pos) > 0:
                    curr_pos[0].close(mslice.close+offset, dd)
                    tradeid += 1
                    curr_pos[0].exit_tradeid = tradeid
                    closed_trades.append(curr_pos[0])
                    curr_pos = []
                    mdf.ix[dd, 'cost'] -= abs(pos) * (offset + mslice.close*tcost)
                new_pos = strat.TradePos([mslice.contract], [1], 1, buytrig, 0)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close+offset, dd)
                curr_pos.append(new_pos)
                pos = 1
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
            elif (mslice.close <= selltrig) and (pos >=0 ):
                if len(curr_pos) > 0:
                    curr_pos[0].close(mslice.close-offset, dd)
                    tradeid += 1
                    curr_pos[0].exit_tradeid = tradeid
                    closed_trades.append(curr_pos[0])
                    curr_pos = []
                    mdf.ix[dd, 'cost'] -= abs(pos) * (offset + mslice.close*tcost)
                new_pos = strat.TradePos([mslice.contract], [1], -1, selltrig, 0)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close-offset, dd)
                curr_pos.append(new_pos)
                pos = -1
                mdf.ix[dd, 'cost'] -= abs(pos) * (offset + mslice.close*tcost)
            mdf.ix[dd, 'pos'] = pos
            
    (res_pnl, ts) = backtest.get_pnl_stats( mdf, start_equity, marginrate, 'm')
    res_trade = backtest.get_trade_stats( closed_trades )
    res = dict( res_pnl.items() + res_trade.items())
    return (res, closed_trades, ts)
    
def run_sim():
    config = {'nearby':1, 
              'rollrule':'-40b', 
              'marginrate':(0.05, 0.05), 
              'capital': 10000,
              'offset': 0,
              'trans_cost': 0.0,
			  'scaler': (2.0, 2.0),
              'file_prefix': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\results\\DualThrust_'}
    

    #commod_list1= ['m','y','a','p','v','l','ru','rb','au','cu','al','zn','ag','i','j','jm'] #
    #start_dates1 = [datetime.date(2010,9,1)] * 9 + [datetime.date(2010,10,1)] * 3 + \
    #            [datetime.date(2012,7,1), datetime.date(2014,1,2), datetime.date(2011,6,1),datetime.date(2013,5,1)]
    #commod_list2 = ['ME', 'CF', 'TA', 'PM', 'RM', 'SR', 'FG', 'OI', 'RI', 'TC', 'WH']
    #start_dates2 = [datetime.date(2012, 2,1)] + [ datetime.date(2012, 6, 1)] * 2 + [datetime.date(2012, 10, 1)] + \
    #            [datetime.date(2013, 2, 1)] * 3 + [datetime.date(2013,6,1)] * 2 + [datetime.date(2013, 10, 1), datetime.date(2014,2,1)]
    #commod_list = commod_list1+commod_list2
    #start_dates = start_dates1 + start_dates2
    #for asset, sdate in zip(commod_list, start_dates):
    asset = 'm'
    start_date = datetime.date(2014,1,1)
    end_date = datetime.date(2014,12,12)
    if asset in ['cu', 'al', 'zn']:
        config['nearby'] = 2
    else:
        config['nearby'] = 1
    freqs = ['5Min', '15Min', '30Min', '60Min', 'D']
    windows = [35]
    aberration( asset, start_date, end_date, scalers, windows, config)

if __name__=="__main__":
    run_sim()
            
