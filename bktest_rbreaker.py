import sys
import misc
import agent
import data_handler as dh
import pandas as pd
import numpy as np
import strategy as strat
import datetime
import backtest

def r_breaker( asset, start_date, end_date, scenarios, freqs, config):
    nearby  = config['nearby']
    rollrule = config['rollrule']
    start_d = misc.day_shift(start_date, '-1b')
    file_prefix = config['file_prefix'] + '_' + asset + '_'
    ddf = misc.nearby(asset, nearby, start_date, end_date, rollrule, 'd', need_shift=True)
    mdf = misc.nearby(asset, nearby, start_date, end_date, rollrule, 'm', need_shift=True)
    mdf = backtest.cleanup_mindata(mdf, asset)
    #ddf = dh.conv_ohlc_freq(mdf, 'D')
    output = {}
    for ix, freq in enumerate(freqs):
        if freq !='1min':
            df = dh.conv_ohlc_freq(mdf, freq)
        else:
            df = mdf
        for iy, k in enumerate(scenarios):
            idx = ix*10+iy
            config['k'] = k
            (res, closed_trades, ts) = r_breaker_sim( ddf, df, config)
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

def r_breaker_sim( ddf, mdf, config):
    marginrate = config['marginrate']
    offset = config['offset']
    k = config['k']
    a = k[0]
    b = k[1]
    c = k[2]
    start_equity = config['capital']
    tcost = config['trans_cost']
    unit = config['unit']
    close_daily = config['close_daily']
    ddf['range'] = (ddf.high - ddf.low).shift(1)
    ddf['ssetup'] = (ddf.high+a*(ddf.close - ddf.low)).shift(1)
    ddf['bsetup'] = (ddf.low-a*(ddf.high - ddf.close)).shift(1)
    ddf['senter'] = ((1+b)*(ddf.high+ddf.close)/2.0 - b * ddf.low).shift(1)
    ddf['benter'] = ((1+b)*(ddf.low+ddf.close)/2.0 - b * ddf.high).shift(1)
    ddf['bbreak'] = ddf.ssetup + c * (ddf.ssetup - ddf.bsetup)
    ddf['sbreak'] = ddf.bsetup - c * (ddf.ssetup - ddf.bsetup)
    ll = mdf.shape[0]
    mdf['pos'] = pd.Series([0]*ll, index = mdf.index)
    mdf['cost'] = pd.Series([0]*ll, index = mdf.index)
    curr_pos = []
    closed_trades = []
    start_d = ddf.index[0]
    end_d = mdf.index[-1].date()
    prev_d = start_d - datetime.timedelta(days=1)
    tradeid = 0
    cur_high = 0
    cur_low = 0
    for dd in mdf.index:
        mslice = mdf.ix[dd]
        min_id = agent.get_min_id(dd)
        d = dd.date()
        dslice = ddf.ix[d]
        if np.isnan(dslice.bbreak):
            continue
        if (prev_d < d):
            num_trades = 0
            cur_high = mslice.high
            cur_low = mslice.low
        else:
            cur_high = max([cur_high, mslice.high])
            cur_low = min([cur_low, mslice.low])
        prev_d = d
        if len(curr_pos) == 0:
            pos = 0
        else:
            pos = curr_pos[0].pos
        mdf.ix[dd, 'pos'] = pos    
        if (min_id >= config['exit_min']):
            if (pos != 0) and (close_daily or (d == end_d)):
                curr_pos[0].close(mslice.close - misc.sign(pos) * offset , dd)
                tradeid += 1
                curr_pos[0].exit_tradeid = tradeid
                closed_trades.append(curr_pos[0])
                curr_pos = []
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost) 
                pos = 0
        elif (min_id <= config['start_min']):
            continue
        else:
            if num_trades >=2:
                continue
            if ((cur_high < dslice.bbreak) and (cur_high >= dslice.ssetup) and (mslice.close < dslice.senter) and (pos >=0)) or \
                    ((cur_low > dslice.sbreak)  and (cur_low  <= dslice.bsetup) and (mslice.close > dslice.benter) and (pos <=0)):
                if len(curr_pos) > 0:
                    curr_pos[0].close(mslice.close-misc.sign(pos)*offset, dd)
                    tradeid += 1
                    curr_pos[0].exit_tradeid = tradeid
                    closed_trades.append(curr_pos[0])
                    curr_pos = []
                    mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
                new_pos = strat.TradePos([mslice.contract], [1], -unit*misc.sign(pos), mslice.close, 0)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close + offset*misc.sign(pos), dd)
                curr_pos.append(new_pos)
                pos = -unit*misc.sign(pos)
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
                num_trades += 1
            elif ((mslice.close >= dslice.bbreak) or (mslice.close <= dslice.sbreak)) and (pos == 0):
                if (mslice.close >= dslice.bbreak):
                    direction = 1
                else:
                    direction = -1
                new_pos = strat.TradePos([mslice.contract], [1], unit*direction, mslice.close, 0)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close + offset*misc.sign(direction), dd)
                curr_pos.append(new_pos)
                pos = unit*direction
                mdf.ix[dd, 'cost'] -=  abs(direction) * (offset + mslice.close*tcost)
                num_trades += 1                
        mdf.ix[dd, 'pos'] = pos
            
    (res_pnl, ts) = backtest.get_pnl_stats( mdf, start_equity, marginrate, 'm')
    res_trade = backtest.get_trade_stats( closed_trades )
    res = dict( res_pnl.items() + res_trade.items())
    return (res, closed_trades, ts)

def run_sim(start_date, end_date, daily_close = True):
    sim_list = [ 'rb','ru','TA','SR','CF','ag','au','cu','i','al','j','zn', 'a', 'jd']
    test_folder = backtest.get_bktest_folder()
    file_prefix = test_folder + 'RBreaker_'
    if daily_close:
        file_prefix = file_prefix + 'daily_'
    config = {'capital': 10000,
              'offset': 0,
              'trans_cost': 0.0,
              'close_daily': daily_close, 
              'unit': 1,
              'min_rng': 0.015, 
              'file_prefix': file_prefix}
    
    scenarios = [(0.25, 0.05, 0.15), (0.30, 0.06, 0.20), (0.35, 0.08, 0.25), (0.4, 0.1, 0.3)]
    freqs = ['1min', '3min', '5min']
    for asset in sim_list:
        sdate =  backtest.sim_start_dict[asset]
        config['marginrate'] = ( backtest.sim_margin_dict[asset], backtest.sim_margin_dict[asset])
        config['rollrule'] = '-50b' 
        config['nearby'] = 1 
        config['start_min'] = 1505
        config['exit_min'] = 2055
        if asset in ['cu', 'al', 'zn']:
            config['nearby'] = 3
            config['rollrule'] = '-1b'
        elif asset in ['IF']:
            config['start_min'] = 1520
            config['exit_min'] = 2110
            config['rollrule'] = '-1b'
        r_breaker( asset, max(sdate, start_date), end_date, scenarios, freqs, config)
    return

if __name__=="__main__":
    args = sys.argv[1:]
    if len(args) < 3:
        d_close = True
    else:
        d_close = (int(args[2])>0)
    if len(args) < 2:
        end_d = datetime.date(2015,1,23)
    else:
        end_d = datetime.datetime.strptime(args[1], '%Y%m%d').date()
    if len(args) < 1:
        start_d = datetime.date(2013,1,2)
    else:
        start_d = datetime.datetime.strptime(args[0], '%Y%m%d').date()
    run_sim(start_d, end_d, d_close)
    pass
            
