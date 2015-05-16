import misc
import data_handler as dh
import pandas as pd
import numpy as np
import strategy as strat
import datetime
import os
import sys
import backtest

NO_OPEN_POS_PROTECT = 30
margin_dict = { 'au': 0.06, 'ag': 0.08, 'cu': 0.07, 'al':0.05,
                'zn': 0.06, 'rb': 0.06, 'ru': 0.12, 'a': 0.05,
                'm':  0.05, 'RM': 0.05, 'y' : 0.05, 'p': 0.05,
                'c':  0.05, 'CF': 0.05, 'i' : 0.05, 'j': 0.05,
                'jm': 0.05, 'pp': 0.05, 'l' : 0.05, 'SR': 0.06,
                'TA': 0.06, 'TC': 0.05, 'ME': 0.06, 'OI': 0.05,
                'v': 0.05, 'IF': 0.1, 'FG':0.06, 'IF': 0.1}

def turtle( asset, start_date, end_date, systems, config):
    rollrule = config['rollrule']
    nearby   = config['nearby']
    file_prefix = config['file_prefix'] + '_' + asset + '_'
    start_d  = misc.day_shift(start_date, '-'+str(max([ max(sys) for sys in systems]))+'b')
    ddf = misc.nearby(asset, nearby, start_d, end_date, rollrule, 'd', need_shift=True)
    mdf = misc.nearby(asset, nearby, start_date, end_date, rollrule, 'm', need_shift=True)
    #ddf = dh.conv_ohlc_freq(mdf, 'D')
    output = {}
    for ix, sys in enumerate(systems):
        config['signals'] = sys
        (res, closed_trades, ts) = turtle_sim( ddf, mdf, config)
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

def turtle_sim( ddf, mdf, config ):
    marginrate = config['marginrate']
    offset = config['offset']
    start_equity = config['capital']
    tcost = config['trans_cost']
    signals = config['signals']
    unit = config['unit']
    NN = config['max_loss']
    max_pos = config['max_pos']
    start_idx = 0
    ddf['ATR'] = pd.Series(dh.ATR(ddf, n=signals[0]).shift(1))
    ddf['OL_1'] = pd.Series(dh.DONCH_H(ddf, signals[0]).shift(1))
    ddf['OS_1'] = pd.Series(dh.DONCH_L(ddf, signals[0]).shift(1))
    ddf['CL_1'] = pd.Series(dh.DONCH_L(ddf, signals[1]).shift(1))
    ddf['CS_1'] = pd.Series(dh.DONCH_H(ddf, signals[1]).shift(1))
    ddf['MA1'] = pd.Series(dh.MA(ddf, signals[2]).shift(1))
    ddf['MA2'] = pd.Series(dh.MA(ddf, signals[3]).shift(1))
    ll = mdf.shape[0]
    mdf['pos'] = pd.Series([0]*ll, index = mdf.index)
    mdf['cost'] = pd.Series([0]*ll, index = mdf.index)
    curr_pos = []
    tradeid = 0
    closed_trades = []
    curr_atr = 0
    for idx, dd in enumerate(mdf.index):
        mslice = mdf.ix[dd]
        d = dd.date()
        dslice = ddf.ix[d]
        tot_pos = sum( [trade.pos for trade in curr_pos] ) 
        mdf.ix[dd, 'pos'] = tot_pos
        if (idx < start_idx) or np.isnan(dslice.ATR):
            continue
        if len(curr_pos) == 0 and idx < len(mdf.index)-NO_OPEN_POS_PROTECT:
            curr_atr = dslice.ATR
            direction = 0
            up_MA = False
            down_MA = False
            if np.isnan(dslice.MA1) or (dslice.MA1 < dslice.MA2):
                up_MA = True
            if np.isnan(dslice.MA1) or (dslice.MA1 > dslice.MA2):
                down_MA = True                
            if (mslice.close >= dslice.OL_1) and up_MA:
                direction = 1
            elif (mslice.close <= dslice.OS_1) and down_MA:
                direction = -1
            pos = direction * unit
            if direction != 0:
                new_pos = strat.TradePos([mslice.contract], [1], pos, mslice.close, mslice.close - direction * curr_atr * NN)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close + direction * offset, dd)
                mdf.ix[dd, 'cost'] -= abs(pos) * (offset + mslice.close*tcost)
                curr_pos.append(new_pos)
                curr_atr = dslice.ATR
        elif (idx >= len(mdf.index)-NO_OPEN_POS_PROTECT):
            if len(curr_pos)>0:
                for trade_pos in curr_pos:
                    trade_pos.close(mslice.close - misc.sign(trade_pos.pos) * offset, dd)
                    tradeid += 1
                    trade_pos.exit_tradeid = tradeid
                    closed_trades.append(trade_pos)
                    mdf.ix[dd, 'cost'] -= abs(trade_pos.pos) * (offset + mslice.close*tcost)
                curr_pos = []
        else:
            direction = curr_pos[0].direction
            #exit position out of channel
            if (direction == 1 and mslice.close <= dslice.CL_1) or \
                    (direction == -1 and mslice.close >= dslice.CS_1):
                for trade_pos in curr_pos:
                    trade_pos.close(mslice.close - misc.sign(trade_pos.pos) * offset, dd)
                    tradeid += 1
                    trade_pos.exit_tradeid = tradeid
                    closed_trades.append(trade_pos)
                    mdf.ix[dd, 'cost'] -= abs(trade_pos.pos) * (offset + mslice.close*tcost)
                curr_pos = []
            #stop loss position partially
            elif (curr_pos[-1].exit_target - mslice.close) * direction >= 0:
                for trade_pos in curr_pos:
                    if (trade_pos.exit_target - mslice.close) * direction > 0:
                        trade_pos.close(mslice.close - misc.sign(trade_pos.pos) * offset, dd)
                        tradeid += 1
                        trade_pos.exit_tradeid = tradeid
                        closed_trades.append(trade_pos)
                        mdf.ix[dd, 'cost'] -= abs(trade_pos.pos) * (offset + mslice.close*tcost)
                curr_pos = [trade for trade in curr_pos if not trade.is_closed]
            #add positions
            elif (len(curr_pos) < max_pos) and (mslice.close - curr_pos[-1].entry_price)*direction > curr_atr/max_pos*NN:
                for trade_pos in curr_pos:
                    #trade.exit_target += curr_atr/max_pos*NN * direction
                    trade_pos.exit_target = mslice.close - direction * curr_atr * NN
                new_pos = strat.TradePos([mslice.contract], [1], direction*unit, mslice.close, mslice.close - direction * curr_atr * NN)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close + direction * offset, dd)
                mdf.ix[dd, 'cost'] -= abs(pos) * (offset + mslice.close*tcost)
                curr_pos.append(new_pos)
        mdf.ix[dd, 'pos'] = sum( [trade.pos for trade in curr_pos] )    

    (res_pnl, ts) = backtest.get_pnl_stats( mdf, start_equity, marginrate, 'm')
    res_trade = backtest.get_trade_stats( closed_trades )
    res = dict( res_pnl.items() + res_trade.items())
    return (res, closed_trades, ts)
    
def run_sim(start_date, end_date):
    test_folder = backtest.get_bktest_folder()
    file_prefix = test_folder + 'Turtle_'
    config = {'capital': 10000,
              'offset': 0,
              'trans_cost': 0.0, 
              'max_loss': 2,
              'max_pos': 4,
              'unit': 1,
              'file_prefix': file_prefix}

    commod_list1 = ['m','y','l','ru','rb','p','cu','al','v','a','au','zn','ag','i','j','jm'] #
    start_dates1 = [datetime.date(2010,10,1)] * 12 + \
                [datetime.date(2012,7,1), datetime.date(2013,11,26), datetime.date(2011,6,1),datetime.date(2013,5,1)]
    commod_list2 = ['ME', 'CF', 'TA', 'PM', 'RM', 'SR', 'FG', 'OI', 'RI', 'TC', 'WH','pp', 'IF']
    start_dates2 = [datetime.date(2012, 2,1)] + [ datetime.date(2012, 6, 1)] * 2 + [datetime.date(2012, 10, 1)] + \
                [datetime.date(2013, 2, 1)] * 3 + [datetime.date(2013,6,1)] * 2 + \
                [datetime.date(2013, 10, 1), datetime.date(2014,2,1), datetime.date(2014,4,1), datetime.date(2010,7,1)]
    commod_list = commod_list1+commod_list2
    start_dates = start_dates1 + start_dates2
    sim_list = ['IF']
    sdate_list = []
    for c, d in zip(commod_list, start_dates):
        if c in sim_list:
            sdate_list.append(d)
    systems = [(20, 10, 40, 10), (20, 10, 40, 5), (20, 10, 30, 5), (20, 10, 30, 10)]
    for asset, sdate in zip(sim_list, sdate_list):
        config['marginrate'] = ( margin_dict[asset], margin_dict[asset]) 
        config['nearby'] = 1
        config['rollrule'] = '-50b'
        if asset in ['cu', 'al', 'zn']:
            config['nearby'] = 3
            config['rollrule'] = '-1b'
        elif asset in ['IF']:
            config['rollrule'] = '-1b'
        elif asset in ['au', 'ag']:
            config['rollrule'] = '-25b'  
        turtle( asset, max(sdate, start_date), end_date, systems, config)
    return 
    
if __name__=="__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        end_d = datetime.date(2014,11,30)
    else:
        end_d = datetime.datetime.strptime(args[1], '%Y%m%d').date()
    if len(args) < 1:
        start_d = datetime.date(2014,1,2)
    else:
        start_d = datetime.datetime.strptime(args[0], '%Y%m%d').date()
    run_sim(start_d, end_d)
