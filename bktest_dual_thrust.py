import sys
import misc
import agent
import data_handler as dh
import pandas as pd
import numpy as np
import strategy as strat
import datetime
import backtest

def dual_thrust( asset, start_date, end_date, scalers, lookbacks, config):
    nearby  = config['nearby']
    rollrule = config['rollrule']
    maxlook = max(lookbacks)
    start_d = misc.day_shift(start_date, '-'+str(maxlook)+'b')
    file_prefix = config['file_prefix'] + '_' + asset + '_'
    ddf = misc.nearby(asset, nearby, start_d, end_date, rollrule, 'd', need_shift=True)
    mdf = misc.nearby(asset, nearby, start_date, end_date, rollrule, 'm', need_shift=True)
    output = {}
    for ix, win in enumerate(lookbacks):
        config['win'] = win
        for iy, k in enumerate(scalers):
            idx = ix*10+iy
            config['k'] = k
            (res, closed_trades, ts) = dual_thrust_sim( ddf, mdf, config)
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

def dual_thrust_sim( ddf, mdf, config):
    close_daily = config['close_daily']
    marginrate = config['marginrate']
    offset = config['offset']
    k = config['k']
    start_equity = config['capital']
    win = config['win']
    tcost = config['trans_cost']
    unit = config['unit']
    ddf['TR'] = pd.concat([pd.rolling_max(ddf.high, win) - pd.rolling_min(ddf.close, win), 
                           pd.rolling_max(ddf.close, win) - pd.rolling_min(ddf.low, win)], 
                           join='outer', axis=1).max(axis=1).shift(1) 
    ll = mdf.shape[0]
    mdf['pos'] = pd.Series([0]*ll, index = mdf.index)
    mdf['cost'] = pd.Series([0]*ll, index = mdf.index)
    curr_pos = []
    closed_trades = []
    start_d = ddf.index[0]
    end_d = mdf.index[-1].date()
    prev_d = start_d - datetime.timedelta(days=1)
    tradeid = 0
    for dd in mdf.index:
        mslice = mdf.ix[dd]
        min_id = agent.get_min_id(dd)
        d = dd.date()
        dslice = ddf.ix[d]
        if len(curr_pos) == 0:
            pos = 0
        else:
            pos = curr_pos[0].pos
        mdf.ix[dd, 'pos'] = pos    
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
        
        if (min_id >= 2055):
            if (pos != 0) and (close_daily or (d == end_d)):
                curr_pos[0].close(mslice.close - misc.sign(pos) * offset , dd)
                tradeid += 1
                curr_pos[0].exit_tradeid = tradeid
                closed_trades.append(curr_pos[0])
                curr_pos = []
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost) 
                pos = 0
        else:
            if (mslice.close >= buytrig) and (pos <=0 ):
                if len(curr_pos) > 0:
                    curr_pos[0].close(mslice.close+offset, dd)
                    tradeid += 1
                    curr_pos[0].exit_tradeid = tradeid
                    closed_trades.append(curr_pos[0])
                    curr_pos = []
                    mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
                new_pos = strat.TradePos([mslice.contract], [1], unit, buytrig, 0)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close + offset, dd)
                curr_pos.append(new_pos)
                pos = unit
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
            elif (mslice.close <= selltrig) and (pos >=0 ):
                if len(curr_pos) > 0:
                    curr_pos[0].close(mslice.close-offset, dd)
                    tradeid += 1
                    curr_pos[0].exit_tradeid = tradeid
                    closed_trades.append(curr_pos[0])
                    curr_pos = []
                    mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
                new_pos = strat.TradePos([mslice.contract], [1], -unit, selltrig, 0)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close - offset, dd)
                curr_pos.append(new_pos)
                pos = -unit
                mdf.ix[dd, 'cost'] -= abs(pos) * (offset + mslice.close*tcost)
        mdf.ix[dd, 'pos'] = pos
            
    (res_pnl, ts) = backtest.get_pnl_stats( mdf, start_equity, marginrate, 'm')
    res_trade = backtest.get_trade_stats( closed_trades )
    res = dict( res_pnl.items() + res_trade.items())
    return (res, closed_trades, ts)

    #commod_list1= ['m','y','a','p','v','l','ru','rb','au','cu','al','zn','ag','i','j','jm'] #
    #start_dates1 = [datetime.date(2010,9,1)] * 9 + [datetime.date(2010,10,1)] * 3 + \
    #            [datetime.date(2012,7,1), datetime.date(2014,1,2), datetime.date(2011,6,1),datetime.date(2013,5,1)]
    #commod_list2 = ['ME', 'CF', 'TA', 'PM', 'RM', 'SR', 'FG', 'OI', 'RI', 'TC', 'WH']
    #start_dates2 = [datetime.date(2012, 2,1)] + [ datetime.date(2012, 6, 1)] * 2 + [datetime.date(2012, 10, 1)] + \
    #            [datetime.date(2013, 2, 1)] * 3 + [datetime.date(2013,6,1)] * 2 + [datetime.date(2013, 10, 1), datetime.date(2014,2,1)]
    #commod_list = commod_list1+commod_list2
    #start_dates = start_dates1 + start_dates2
        
def run_sim(asset, start_date, end_date, daily_close):
    file_prefix = 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\results\\DT_'
    if daily_close:
        file_prefix = file_prefix + 'daily_'
    config = {'nearby':1, 
              'rollrule':'-40b', 
              'marginrate':(0.05, 0.05), 
              'capital': 10000,
              'offset': 0,
              'trans_cost': 0.0,
              'close_daily': daily_close, 
              'unit': 1,
              'file_prefix': file_prefix }
    
    if asset in ['cu', 'al', 'zn']:
        config['nearby'] = 3
        config['rollrule'] = '-1b'
    elif asset in ['IF']:
        config['rollrule'] = '-1b'
    scalers = [(0.3, 0.3), (0.5,0.5), (0.7,0.7), (0.9, 0.9)]
    lookbacks = [1, 2, 4]
    dual_thrust( asset, start_date, end_date, scalers, lookbacks, config)
    return

if __name__=="__main__":
    args = sys.argv[1:]
    if len(args) < 4:
        d_close = False
    else:
        d_close = (int(args[3])>0)
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
    run_sim(asset, start_d, end_d, d_close)
            
