import sys
import misc
import agent
import data_handler as dh
import pandas as pd
import numpy as np
import strategy as strat
import datetime
import backtest

def dual_thrust( asset, start_date, end_date, scenarios, config, channels=[20]):
    nearby  = config['nearby']
    rollrule = config['rollrule']
    start_d = misc.day_shift(start_date, '-4b')
    file_prefix = config['file_prefix'] + '_' + asset + '_'
    #print asset, nearby, start_d, end_date
    ddf = misc.nearby(asset, nearby, start_d, end_date, rollrule, 'd', need_shift=True)
    mdf = misc.nearby(asset, nearby, start_d, end_date, rollrule, 'm', need_shift=True)
    mdf = backtest.cleanup_mindata(mdf, asset)
    #ddf = dh.conv_ohlc_freq(mdf, 'D')
    output = {}
    for chan in channels:
        for ix, s in enumerate(scenarios):
            config['win'] = s[1]
            config['k'] = s[0]
            config['m'] = s[2]
            idx = chan*100+ix
            config['chan'] = chan
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
    ep_enabled = config['EP']
    start_equity = config['capital']
    win = config['win']
    chan = config['chan']
    chan_func = config['channel_func']
    upper_chan_func = chan_func[0]
    lower_chan_func = chan_func[1]
    multiplier = config['m']
    tcost = config['trans_cost']
    unit = config['unit']
    SL = config['stoploss']
    min_rng = config['min_range']
    no_trade_set = config['no_trade_set']
    if win == -1:
        tr= pd.concat([ddf.high - ddf.low, ddf.close - ddf.close.shift(1)], 
                       join='outer', axis=1).max(axis=1).shift(1)
    elif win == 0:
        tr = pd.concat([(pd.rolling_max(ddf.high, 2) - pd.rolling_min(ddf.close, 2))*multiplier, 
                        (pd.rolling_max(ddf.close, 2) - pd.rolling_min(ddf.low, 2))*multiplier,
                        ddf.high - ddf.close, 
                        ddf.close - ddf.low], 
                        join='outer', axis=1).max(axis=1).shift(1)
    else:
        tr= pd.concat([pd.rolling_max(ddf.high, win) - pd.rolling_min(ddf.close, win), 
                       pd.rolling_max(ddf.close, win) - pd.rolling_min(ddf.low, win)], 
                       join='outer', axis=1).max(axis=1).shift(1)
    ddf['TR'] = tr
    ddf['H1'] = upper_chan_func(ddf, chan).shift(1)
    ddf['L1'] = lower_chan_func(ddf, chan).shift(1)
    #ddf['prev_high'] = ddf.high.shift(1)
    #ddf['prev_low'] = ddf.low.shift(1)    
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
        if np.isnan(dslice.TR) or (mslice.close == 0):
            continue
        if (mslice.low == 0):
            mslice.low = mslice.close
        if mslice.high >= mslice.open * 1.2:
            mslice.high = mslice.close
        if len(curr_pos) == 0:
            pos = 0
        else:
            pos = curr_pos[0].pos
        mdf.ix[dd, 'pos'] = pos
        d_open = dslice.open
        if (prev_d < d):
            d_open = mslice.open
            d_high = mslice.high
            d_low =  mslice.low
        else:
            d_open = dslice.open
            d_high = max(d_high, mslice.high)
            d_low  = min(d_low, mslice.low)
        if (d_open <= 0):
            continue
        prev_d = d
        buytrig  = d_open + max(min_rng * d_open, dslice.TR * k)
        selltrig = d_open - max(min_rng * d_open, dslice.TR * k)
        if ep_enabled:
            buytrig = max(buytrig, d_high)
            selltrig = min(selltrig, d_low)
        if (min_id >= config['exit_min']) :
            if (pos != 0) and (close_daily or (d == end_d)):
                curr_pos[0].close(mslice.close - misc.sign(pos) * offset , dd)
                tradeid += 1
                curr_pos[0].exit_tradeid = tradeid
                closed_trades.append(curr_pos[0])
                curr_pos = []
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost) 
                pos = 0
        elif min_id not in no_trade_set:
            if (pos!=0) and (SL>0):
                curr_pos[0].trail_update(mslice.close)
                if curr_pos[0].check_exit(mslice.close, SL*mslice.close):
                    curr_pos[0].close(mslice.close-offset*misc.sign(pos), dd)
                    tradeid += 1
                    curr_pos[0].exit_tradeid = tradeid
                    closed_trades.append(curr_pos[0])
                    curr_pos = []
                    mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)    
                    pos = 0
            if (mslice.high >= buytrig) and (pos <=0 ):
                if len(curr_pos) > 0:
                    curr_pos[0].close(mslice.close+offset, dd)
                    tradeid += 1
                    curr_pos[0].exit_tradeid = tradeid
                    closed_trades.append(curr_pos[0])
                    curr_pos = []
                    mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
                if mslice.high >= dslice.H1:
                    new_pos = strat.TradePos([mslice.contract], [1], unit, mslice.close + offset, mslice.close + offset)
                    tradeid += 1
                    new_pos.entry_tradeid = tradeid
                    new_pos.open(mslice.close + offset, dd)
                    curr_pos.append(new_pos)
                    pos = unit
                    mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
            elif (mslice.low <= selltrig) and (pos >=0 ):
                if len(curr_pos) > 0:
                    curr_pos[0].close(mslice.close-offset, dd)
                    tradeid += 1
                    curr_pos[0].exit_tradeid = tradeid
                    closed_trades.append(curr_pos[0])
                    curr_pos = []
                    mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
                if mslice.low <= dslice.L1:
                    new_pos = strat.TradePos([mslice.contract], [1], -unit, mslice.close - offset, mslice.close - offset)
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
        
def run_sim(start_date, end_date, daily_close = False):
    #sim_list = [ 'a', 'm', 'p', 'y', 'cs', 'i', 'rb',  'SR', 'MA', 'l', 'TA', 'MA', 'pp', 'TF']
    sim_list = ['SR', 'i', 'TF', 'l', 'm', 'y', 'p', 'TA', 'jd']
    #sim_list = [ 'a', 'm', 'p', 'y', 'cs', 'i', 'rb',  'SR', 'MA', 'l', 'TA', 'MA', 'pp', 'TF']
    test_folder = backtest.get_bktest_folder()
    file_prefix = test_folder + 'test/DTchan1'
    if daily_close:
        file_prefix = file_prefix + 'daily_'
    #file_prefix = file_prefix + '_'
    config = {'capital': 10000,
              'offset': 0,
              'trans_cost': 0.0,
              'close_daily': daily_close, 
              'unit': 1,
              'stoploss': 0.0,
              'min_range': 0.00,
              'EP': False,
              'channel_func': [dh.DONCH_H, dh.DONCH_L],
              'file_prefix': file_prefix}
    
    scenarios = [ (0.5, 1, 0), (0.6, 1, 0), (0.7, 1, 0), (0.8, 1, 0), (0.9, 1, 0), (1.0, 1, 0), (1.1, 1, 0)]
    channels = [5, 10, 15, 20, 25]
    for asset in sim_list:
        sdate =  backtest.sim_start_dict[asset]
        config['marginrate'] = ( backtest.sim_margin_dict[asset], backtest.sim_margin_dict[asset])
        config['nearby'] = 1
        config['rollrule'] = '-50b'
        config['exit_min'] = 2055
        config['no_trade_set'] = range(300, 301) + range(1500, 1501) + range(2059, 2100)
        if asset in ['cu', 'al', 'zn']:
            config['nearby'] = 3
            config['rollrule'] = '-1b'
        elif asset in ['IF', 'IH', 'IC']:
            config['rollrule'] = '-2b'
            config['no_trade_set'] = range(1515, 1520) + range(2110, 2115)
        elif asset in ['au', 'ag']:
            config['rollrule'] = '-25b'
        elif asset in ['TF', 'T']:
            config['rollrule'] = '-20b'
            config['no_trade_set'] = range(1515, 1520) + range(2110, 2115)
        config['no_trade_set'] = []
        dual_thrust( asset, max(sdate, start_date), end_date, scenarios, config, channels = channels)
    return

if __name__=="__main__":
    args = sys.argv[1:]
    if len(args) < 3:
        d_close = False
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
