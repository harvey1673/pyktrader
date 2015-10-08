import misc
import agent
import data_handler as dh
import pandas as pd
import numpy as np
import strategy as strat
import datetime
import backtest
import sys

def chanbreak( asset, start_date, end_date, freqs, windows, config):
    nearby  = config['nearby']
    rollrule = config['rollrule']
    file_prefix = config['file_prefix'] + '_' + asset + '_'
    mdf = misc.nearby(asset, nearby, start_d, end_date, rollrule, 'm', need_shift=True)    
    mdf = backtest.cleanup_mindata(mdf, asset)
    output = {}
    for ix, freq in enumerate(freqs):
        config['freq'] = freq
        for iy, win in enumerate(windows): 
            idx = ix*10+iy
            config['win'] = win
            (res, closed_trades, ts) = chanbreak_sim( mdf, config)
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

def chanbreak_sim( mdf, config):
    freq = config['freq']
    str_freq = str(freq) + 'Min'
    xdf = dh.conv_ohlc_freq(mdf, str_freq)
    start_equity = config['capital']
    tcost = config['trans_cost']
    unit = config['unit']
    k = config['scaler']
    d_close = config['daily_close']
    marginrate = config['marginrate']
    offset = config['offset']
    win = config['win']
    chan_func = config['channel_func']
    no_trade_set = config['no_trade_set']
    upper_chan_func = chan_func[0]
    lower_chan_func = chan_func[1]
    entry_chan = win    
    exit_chan = int(entry_chan/k[1])
    xdf['H1'] = upper_chan_func(xdf, entry_chan).shift(1)
    xdf['L1'] = lower_chan_func(xdf, entry_chan).shift(1)
    xdf['H2'] = upper_chan_func(xdf, exit_chan).shift(1)
    xdf['L2'] = lower_chan_func(xdf, exit_chan).shift(1)
    xdf['ATR'] = dh.ATR(xdf, entry_chan).shift(1)
    df = mdf.join(xdf, how = 'left').fillna(method='ffill')
    df['date'] = df.index.date
    ll = df.shape[0]
    df['pos'] = pd.Series([0]*ll, index = df.index)
    df['cost'] = pd.Series([0]*ll, index = df.index)
    curr_pos = []
    closed_trades = []
    end_d = df['date'][-1]
    tradeid = 0
    for idx, dd in enumerate(df.index):
        mslice = df.ix[dd]
        min_id = agent.get_min_id(dd)
        d = mslice.date
        if len(curr_pos) == 0:
            pos = 0
        else:
            pos = curr_pos[0].pos
        df.ix[dd, 'pos'] = pos
        if np.isnan(mslice.ATR):
            continue
        if (min_id >=config['exit_min']):
            if (pos!=0) and ((d == end_d) or (d_close)):
                curr_pos[0].close(mslice.close - misc.sign(pos) * offset , dd)
                tradeid += 1
                curr_pos[0].exit_tradeid = tradeid
                closed_trades.append(curr_pos[0])
                curr_pos = []
                df.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost) 
            continue
        else:
            if (pos !=0):
                curr_pos[0].trail_update(mslice.close)
                if curr_pos[0].trail_check(mslice.close, mslice.ATR*k[0]):
                    curr_pos[0].close(mslice.close - misc.sign(pos) * offset, dd)
                    tradeid += 1
                    curr_pos[0].exit_tradeid = tradeid
                    closed_trades.append(curr_pos[0])
                    pos = 0
                    curr_pos = []                    
            if ((mslice.close >= mslice.H2) and (pos<0)) or ((mslice.close <= mslice.L2) and (pos>0)):
                curr_pos[0].close(mslice.close - misc.sign(pos) * offset, dd)
                tradeid += 1
                curr_pos[0].exit_tradeid = tradeid
                closed_trades.append(curr_pos[0])
                curr_pos = []
                df.ix[dd, 'cost'] -= abs(pos) * (offset + mslice.close*tcost)
                pos = 0
            if ((mslice.close>=mslice.H1) and (pos<=0)) or ((mslice.close <= mslice.L1) and (pos>=0)):
                if (pos ==0 ):
                    target_pos = (mslice.close>=mslice.H1) * unit -(mslice.close<=mslice.L1) * unit
                    new_pos = strat.TradePos([mslice.contract], [1], target_pos, mslice.close, mslice.close)
                    tradeid += 1
                    new_pos.entry_tradeid = tradeid
                    new_pos.open(mslice.close + misc.sign(target_pos)*offset, dd)
                    curr_pos.append(new_pos)
                    df.ix[dd, 'cost'] -=  abs(target_pos) * (offset + mslice.close*tcost)
                    df.ix[dd, 'pos'] = pos
                else:
                    print "something wrong with position=%s, close =%s, upBnd=%s, lowBnd=%s" % ( pos, mslice.close, xslice.H1, xslice.L1)
            
    (res_pnl, ts) = backtest.get_pnl_stats( mdf, start_equity, marginrate, 'm')
    res_trade = backtest.get_trade_stats( closed_trades )
    res = dict( res_pnl.items() + res_trade.items())
    return (res, closed_trades, ts)
    
def run_sim(start_date, end_date, daily_close):
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
    sim_list = [ 'm', 'y', 'l', 'ru', 'rb', 'TA', 'SR', 'RM', 'cu']
    sdate_list = []
    for c, d in zip(commod_list, start_dates):
        if c in sim_list:
            sdate_list.append(d)
    
    test_folder = backtest.get_bktest_folder()
    file_prefix = test_folder + 'ChanBreak_'
    config = {'capital': 10000,
              'offset': 0,
              'trans_cost': 0.0, 
              'unit': 1,
              'scaler': (0.5, 2),
              'channel_func': [dh.DONCH_H, dh.DONCH_L],
              'daily_close': daily_close,
              'file_prefix': file_prefix}        
    freqs = [3, 5, ]
    windows = [20, 40, 60, 120, 270]
    for asset, sdate in zip(sim_list, sdate_list):
        config['marginrate'] = ( backtest.sim_margin_dict[asset], backtest.sim_margin_dict[asset])
        config['rollrule'] = '-50b' 
        config['nearby'] = 1 
        config['start_min'] = 1600
        config['exit_min'] = 2055
        config['no_trade_set'] = range(300, 302) + range(1500, 1502) + range(2058, 2100)
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
        chanbreak( asset, start_date, end_date, freqs, windows, config)

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
