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

def turtle( asset, start_date, end_date, systems, config):
    rollrule = config['rollrule']
    nearby   = config['nearby']
    file_prefix = config['file_prefix'] + '_' + asset + '_'
    start_d  = misc.day_shift(start_date, '-'+str(max([ max(sys) for sys in systems]))+'b')
    #ddf = misc.nearby(asset, nearby, start_d, end_date, rollrule, 'd', need_shift=True)
    mdf = misc.nearby(asset, nearby, start_d, end_date, rollrule, 'm', need_shift=True)
    ddf = dh.conv_ohlc_freq(mdf, 'D')
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
            if mslice.close   >= dslice.OL_1:
                direction = 1
            elif mslice.close <= dslice.OS_1:
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
    
def run_sim(asset, start_date, end_date):
    config = {'nearby':1, 
              'rollrule':'-40b', 
              'marginrate':(0.05, 0.05), 
              'capital': 10000,
              'offset': 0,
              'trans_cost': 0.0, 
              'max_loss': 2,
              'max_pos': 4,
              'unit': 1,
              'file_prefix': 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\results\\Turtle_'}

    # commod_list1= ['m','y','a','p','v','l','ru','rb','au','cu','al','zn','ag','i','j','jm'] #
    # start_dates1 = [datetime.date(2010,9,1)] * 9 + [datetime.date(2010,10,1)] * 3 + \
                # [datetime.date(2012,7,1), datetime.date(2014,1,2), datetime.date(2011,6,1),datetime.date(2013,5,1)]
    # commod_list2 = ['ME', 'CF', 'TA', 'PM', 'RM', 'SR', 'FG', 'OI', 'RI', 'TC', 'WH']
    # start_dates2 = [datetime.date(2012, 2,1)] + [ datetime.date(2012, 6, 1)] * 2 + [datetime.date(2012, 10, 1)] + \
                # [datetime.date(2013, 2, 1)] * 3 + [datetime.date(2013,6,1)] * 2 + [datetime.date(2013, 10, 1), datetime.date(2014,2,1)]
    # commod_list = commod_list1+commod_list2
    # start_dates = start_dates1 + start_dates2
    if asset in ['cu', 'al', 'zn']:
        config['nearby'] = 2
    else:
        config['nearby'] = 1
    systems = [(20,10), (15,7),(40,20)]
    turtle( asset, start_date, end_date, systems, config)
    return 
    
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
