import misc
import agent
import sys
import data_handler as dh
import pandas as pd
import numpy as np
import strategy as strat
import datetime
import backtest

def fisher_swing( asset, start_date, end_date, freqs, windows, config):
    nearby  = config['nearby']
    rollrule = config['rollrule']
    file_prefix = config['file_prefix'] + '_' + asset + '_'
    df = misc.nearby(asset, nearby, start_date, end_date, rollrule, 'm', need_shift=True)    
    output = {}
    for ix, freq in enumerate(freqs):
        xdf = dh.conv_ohlc_freq(df, freq)
        for iy, win in enumerate(windows):
            idx = ix*10+iy
            config['win'] = win
            (res, closed_trades, ts) = fisher_swing_sim( xdf, config)
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

def fisher_swing_sim( df, config):
    marginrate = config['marginrate']
    offset = config['offset']
    win = config['win']
    start_equity = config['capital']
    tcost = config['trans_cost']
    unit = config['unit']
    fisher = dh.FISHER(df, win[0]).shift(1)
    df['FISHER_I'] = fisher['FISHER_I']
    df = df.join(dh.BBANDS_STOP(df, win[1], 1.0))
    ha_df = dh.HEIKEN_ASHI(df, win[2])
    df['HAopen'] = ha_df['HAopen']
    df['HAclose'] = ha_df['HAclose']
    ll = df.shape[0]
    df['pos'] = pd.Series([0]*ll, index = df.index)
    df['cost'] = pd.Series([0]*ll, index = df.index)
    curr_pos = []
    closed_trades = []
    end_d = df.index[-1].date()
    tradeid = 0
    for dd in df.index:
        mslice = df.ix[dd]
        min_id = agent.get_min_id(dd)
        d = dd.date()
        if len(curr_pos) == 0:
            pos = 0
        else:
            pos = curr_pos[0].pos
        df.ix[dd, 'pos'] = pos
        if np.isnan(mslice.BBSTOP_lower) or np.isnan(mslice.FISHER_I) or np.isnan(mslice.HAclose):
            continue
        end_trading = (min_id >=config['exit_min']) and (d == end_d)
        stop_loss = (pos > 0) and ((mslice.close < mslice.BBSTOP_lower) or (mslice.FISHER_I<0))
        stop_loss = stop_loss or ((pos < 0) and ((mslice.close > mslice.BBSTOP_upper) or (mslice.FISHER_I>0)))
        start_long = (mslice.FISHER_I>0) and (mslice.HAclose > mslice.HAopen ) and (mslice.BBSTOP_trend > 0)
        start_short = (mslice.FISHER_I<0) and (mslice.HAclose < mslice.HAopen ) and (mslice.BBSTOP_trend < 0)
        if pos != 0:
            if stop_loss or end_trading:
                curr_pos[0].close(mslice.close - misc.sign(pos) * offset , dd)
                tradeid += 1
                curr_pos[0].exit_tradeid = tradeid
                closed_trades.append(curr_pos[0])
                curr_pos = []
                df.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)    
                pos = 0
        if (not end_trading) and (pos == 0):
            if start_long and start_short:
                print "warning: get both long and short signal, something is wrong!"
                print mslice
                continue
            pos = (start_long == True) * unit - (start_short == True) * unit
            if abs(pos)>0:
                #target = (start_long == True) * mslice.close +(start_short == True) * mslice.close
                new_pos = strat.TradePos([mslice.contract], [1], pos, mslice.close, mslice.close)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close + misc.sign(pos)*offset, dd)
                curr_pos.append(new_pos)
                df.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
        df.ix[dd, 'pos'] = pos
            
    (res_pnl, ts) = backtest.get_pnl_stats( df, start_equity, marginrate, 'm')
    res_trade = backtest.get_trade_stats( closed_trades )
    res = dict( res_pnl.items() + res_trade.items())
    return (res, closed_trades, ts)
    
def run_sim(start_date, end_date):
    commod_list1 = ['m','y','l','ru','rb','p','cu','al','v','a','au','zn','ag','i','j','jm'] #
    start_dates1 = [datetime.date(2010,10,1)] * 12 + \
                [datetime.date(2012,7,1), datetime.date(2013,11,26), datetime.date(2011,6,1),datetime.date(2013,5,1)]
    commod_list2 = ['ME', 'CF', 'TA', 'PM', 'RM', 'SR', 'FG', 'OI', 'RI', 'TC', 'WH', 'IF']
    start_dates2 = [datetime.date(2012, 2,1)] + [ datetime.date(2012, 6, 1)] * 2 + [datetime.date(2012, 10, 1)] + \
                [datetime.date(2013, 2, 1)] * 3 + [datetime.date(2013,6,1)] * 2 + \
                [datetime.date(2013, 10, 1), datetime.date(2014,2,1), datetime.date(2010,6,1)]
    commod_list = commod_list1 + commod_list2
    start_dates = start_dates1 + start_dates2
    #sim_list = ['m', 'y', 'l', 'ru', 'rb', 'TA', 'SR', 'CF','ME', 'RM', 'ag', 'au', 'cu', 'al', 'zn'] 
    sim_list = [ 'IF','ru', 'rb', 'a', 'j', 'p','pp','zn', 'al', 'SR', 'ME', 'CF', 'RM']
    sdate_list = []
    for c, d in zip(commod_list, start_dates):
        if c in sim_list:
            sdate_list.append(d)
    file_prefix = 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\results\\FisherSwing_'
    #if daily_close:
    #    file_prefix = file_prefix + 'daily_'
    config = {'capital': 10000,
              'offset': 0,
              'trans_cost': 0.0, 
              'unit': 1,
              'scaler': (2.0, 2.0),
              'file_prefix': file_prefix}        

    freqs = ['5Min', '15Min', '30Min', '60Min','120Min', 'D']
    windows = [[30, 20, 6], [20, 15, 6]]
    for asset, sdate in zip(sim_list, sdate_list):
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
        fisher_swing( asset, max(start_date, sdate), end_date, freqs, windows, config)

if __name__=="__main__":
    args = sys.argv[1:]
    #if len(args) < 3:
    #    d_close = True
    #else:
    #    d_close = (int(args[2])>0)
    if len(args) < 2:
        end_d = datetime.date(2015,1,23)
    else:
        end_d = datetime.datetime.strptime(args[1], '%Y%m%d').date()
    if len(args) < 1:
        start_d = datetime.date(2013,1,2)
    else:
        start_d = datetime.datetime.strptime(args[0], '%Y%m%d').date()
    run_sim(start_d, end_d)
    pass
