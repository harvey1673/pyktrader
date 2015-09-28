import sys
import misc
import agent
import data_handler as dh
import pandas as pd
import numpy as np
import strategy as strat
import datetime
import backtest

def ohlcsum(df):
    df = df.sort()
    return pd.Series([df.index[0], df['open'][0], df['high'].max(), df['low'].min(), df['close'][-1], df['volume'].sum()],
                  index = ['datetime', 'open','high','low','close','volume'])

def dual_thrust( asset, start_date, end_date, scenarios, config):
    nearby  = config['nearby']
    rollrule = config['rollrule']
    start_d = misc.day_shift(start_date, '-2b')
    file_prefix = config['file_prefix'] + '_' + asset + '_'
    mdf = misc.nearby(asset, nearby, start_d, end_date, rollrule, 'm', need_shift=True)
    mdf = backtest.cleanup_mindata(mdf, asset)
    output = {}
    for ix, s in enumerate(scenarios):
        config['win'] = s[1]
        config['k'] = s[0]
        config['m'] = s[2]
        config['f'] = s[3]
        (res, closed_trades, ts) = dual_thrust_sim( mdf, config)
        output[ix] = res
        print 'saving results for scen = %s' % str(ix)
        all_trades = {}
        for i, tradepos in enumerate(closed_trades):
            all_trades[i] = strat.tradepos2dict(tradepos)
        fname = file_prefix + str(ix) + '_trades.csv'
        trades = pd.DataFrame.from_dict(all_trades).T  
        trades.to_csv(fname)
        fname = file_prefix + str(ix) + '_dailydata.csv'
        ts.to_csv(fname)
    fname = file_prefix + 'stats.csv'
    res = pd.DataFrame.from_dict(output)
    res.to_csv(fname)
    return 

def dual_thrust_sim( mdf, config):
    close_daily = config['close_daily']
    marginrate = config['marginrate']
    offset = config['offset']
    k = config['k']
    f = config['f']
    start_equity = config['capital']
    win = config['win']
    multiplier = config['m']
    tcost = config['trans_cost']
    unit = config['unit']
    SL = config['stoploss']
    min_rng = config['min_range']
    ma_fast = config['MA_fast']
    ll = mdf.shape[0]
    mdf['min_idx'] = pd.Series(1, index = mdf.index)
    mdf.loc[mdf['min_id']<1500, 'min_idx'] = 0
    mdf['date_idx'] = mdf.index.date
    xdf = mdf.groupby([mdf['date_idx'], mdf['min_idx']]).apply(ohlcsum).reset_index().set_index('datetime')
    if win == -1:
        tr= pd.concat([xdf.high - xdf.low, abs(xdf.close - xdf.close.shift(1))], 
                       join='outer', axis=1).max(axis=1).shift(1)
    elif win == -2:
        tr= pd.rolling_max(xdf.high, 2) - pd.rolling_min(xdf.low, 2)                       
    elif win == 0:
        tr = pd.concat([(pd.rolling_max(xdf.high, 2) - pd.rolling_min(xdf.close, 2))*multiplier, 
                        (pd.rolling_max(xdf.close, 2) - pd.rolling_min(xdf.low, 2))*multiplier,
                        xdf.high - xdf.close, 
                        xdf.close - xdf.low], 
                        join='outer', axis=1).max(axis=1).shift(1)
    else:
        tr= pd.concat([pd.rolling_max(xdf.high, win) - pd.rolling_min(xdf.close, win), 
                       pd.rolling_max(xdf.close, win) - pd.rolling_min(xdf.low, win)], 
                       join='outer', axis=1).max(axis=1).shift(1)
    xdf['TR'] = tr
    xdf['MA'] = pd.rolling_mean(xdf.close, ma_fast).shift(1)
    ddf = pd.concat([xdf['TR'], xdf['MA'], xdf['open'], xdf['date_idx']], axis=1, keys=['TR','MA','dopen', 'date']).fillna(0)
    mdf = mdf.join(ddf, how = 'left').fillna(method='ffill')
    mdf['pos'] = pd.Series([0]*ll, index = mdf.index)
    mdf['cost'] = pd.Series([0]*ll, index = mdf.index)
    curr_pos = []
    closed_trades = []
    start_d = ddf.index[0]
    end_d = mdf.index[-1].date()
    #prev_d = start_d - datetime.timedelta(days=1)
    tradeid = 0
    for dd in mdf.index:
        mslice = mdf.ix[dd]
        min_id = agent.get_min_id(dd)
        if len(curr_pos) == 0:
            pos = 0
        else:
            pos = curr_pos[0].pos
        mdf.ix[dd, 'pos'] = pos    
        if mslice.TR == 0 or mslice.MA == 0:
            continue
        d_open = mslice.dopen
        #if (prev_d < d):
        #    d_open = mslice.open
        #else:
        #    d_open = dslice.open
        rng = max(min_rng * d_open, k * mslice.TR)
        if (d_open <= 0):
            continue
        buytrig  = d_open + k * rng
        selltrig = d_open - k * rng
        if mslice.MA > mslice.close:
            buytrig  += f * k * rng
        elif mslice.MA < mslice.close:
            selltrig -= f * k * rng      
        if (min_id >= config['exit_min']) and (close_daily or (mslice.date == end_d)):
            if (pos != 0):
                curr_pos[0].close(mslice.close - misc.sign(pos) * offset , dd)
                tradeid += 1
                curr_pos[0].exit_tradeid = tradeid
                closed_trades.append(curr_pos[0])
                curr_pos = []
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost) 
                pos = 0
        else:
            if (pos!=0) and (SL>0):
                curr_pos[0].trail_update(mslice.close)
                if (curr_pos[0].trail_check(mslice.close, SL*mslice.close)):
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
    commod_list1 = ['m','y','l','ru','rb','p','cu','al','v','a','au','zn','ag','i','j','jm'] #
    start_dates1 = [datetime.date(2010,10,1)] * 12 + \
                [datetime.date(2012,7,1), datetime.date(2013,11,26), datetime.date(2011,6,1),datetime.date(2013,5,1)]
    commod_list2 = ['ME', 'CF', 'TA', 'PM', 'RM', 'SR', 'FG', 'OI', 'RI', 'TC', 'WH','pp', 'IF', 'MA', 'TF','IH', 'IC']
    start_dates2 = [datetime.date(2012, 2,1)] + [ datetime.date(2012, 6, 1)] * 2 + [datetime.date(2012, 10, 1)] + \
                [datetime.date(2013, 2, 1)] * 3 + [datetime.date(2013,6,1)] * 2 + \
                [datetime.date(2013, 10, 1), datetime.date(2014,2,1), datetime.date(2014,4,1), datetime.date(2010,7,1)] + \
                [datetime.date(2015,1,3), datetime.date(2014,4,1), datetime.date(2015,5,1), datetime.date(2015,5,1)]
    commod_list = commod_list1 + commod_list2
    start_dates = start_dates1 + start_dates2
    sim_list = [ 'y', 'm', 'p', 'RM', 'MA', 'TA', 'a', 'rb', 'ru', 'i', 'j', 'jm', 'cu', 'al', 'zn', 'ag', 'SR', 'CF']
    sdate_list = []
    for c, d in zip(commod_list, start_dates):
        if c in sim_list:
            sdate_list.append(d)
    test_folder = backtest.get_bktest_folder()
    file_prefix = test_folder + 'test/DT_split_'
    if daily_close:
        file_prefix = file_prefix + 'daily_'
    #file_prefix = file_prefix + '_'
    config = {'capital': 10000,
              'offset': 0,
              'MA_fast': 10,
              'MA_slow': 20,
              'trans_cost': 0.0,
              'close_daily': daily_close, 
              'unit': 1,
              'stoploss': 0.0,
              'min_range': 0.004,
              'file_prefix': file_prefix}
    
    scenarios = [ (0.5, 0, 0.5, 0.0), (0.6, 0, 0.5, 0.0), (0.7, 0, 0.5, 0.0), (0.8, 0, 0.5, 0.0),\
                  (0.9, 0, 0.5, 0.0), (1.0, 0, 0.5, 0.0), (1.1, 0, 0.5, 0.0), (1.2, 0, 0.5, 0.0),\
                  (0.5, 1, 0.5, 0.0), (0.6, 1, 0.5, 0.0), (0.7, 1, 0.5, 0.0), (0.8, 1, 0.5, 0.0),\
                  (0.9, 1, 0.5, 0.0), (1.0, 1, 0.5, 0.0), (1.1, 1, 0.5, 0.0), (1.2, 1, 0.5, 0.0),\
                  (0.2, 2, 0.5, 0.0), (0.25,2, 0.5, 0.0), (0.3, 2, 0.5, 0.0), (0.4, 2, 0.5, 0.0),\
                  (0.5, 2, 0.5, 0.0), (0.6, 2, 0.5, 0.0), (0.7, 2, 0.5, 0.0), (0.8, 2, 0.5, 0.0), \
                  (0.2, 2, 0.5, 0.0), (0.25,4, 0.5, 0.0), (0.3, 4, 0.5, 0.0), (0.4, 4, 0.5, 0.0),\
                  (0.5, 2, 0.5, 0.0), (0.6, 4, 0.5, 0.0), (0.7, 4, 0.5, 0.0), (0.8, 4, 0.5, 0.0), \
                  ]
    for asset, sdate in zip(sim_list, sdate_list):
        config['marginrate'] = ( backtest.sim_margin_dict[asset], backtest.sim_margin_dict[asset]) 
        config['nearby'] = 1
        config['rollrule'] = '-50b'
        config['exit_min'] = 2112
        if asset in ['cu', 'al', 'zn']:
            config['nearby'] = 3
            config['rollrule'] = '-1b'
        elif asset in ['IF', 'IH', 'IC']:
            config['rollrule'] = '-2b'
        elif asset in ['au', 'ag']:
            config['rollrule'] = '-25b'
        elif asset in ['TF', 'T']:
            config['rollrule'] = '-20b'
        dual_thrust( asset, max(sdate, start_date), end_date, scenarios, config)
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
