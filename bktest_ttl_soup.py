import sys
import misc
import json
import data_handler as dh
import pandas as pd
import numpy as np
import strategy as strat
import datetime
import backtest

def ttl_soup_sim( mdf, config):
    close_daily = config['close_daily']
    marginrate = config['marginrate']
    offset = config['offset']
    pos_update = config['pos_update']
    pos_class = config['pos_class']
    pos_args  = config['pos_args']
    proc_func = config['proc_func']
    proc_args = config['proc_args']
    start_equity = config['capital']
    tcost = config['trans_cost']
    unit = config['unit']
    SL = config['stoploss']
    chan = config['chan']
    exit_ratio = config['exit_ratio']
    exit_chan = int(chan * exit_ratio)
    gap_win = config['gap_win']
    no_trade_set = config['no_trade_set']
    ll = mdf.shape[0]
    xdf = proc_func(mdf, **proc_args)
    donch_data = dh.DONCH_IDX(xdf, chan)
    hh_str = 'DONCH_H%s' % str(chan)
    hidx_str = 'DONIDX_H%s' % str(chan)
    ll_str = 'DONCH_L%s' % str(chan)
    lidx_str = 'DONIDX_L%s' % str(chan)
    xdf['exit_hh'] = pd.rolling_max(xdf.high, exit_chan)
    xdf['exit_ll'] = pd.rolling_min(xdf.low, exit_chan)
    xdf['ssetup'] = (xdf['close'] >= donch_data[hh_str].shift(1)) & (donch_data[hidx_str]>=gap_win)
    xdf['bsetup'] = (xdf['close'] <= donch_data[ll_str].shift(1)) & (donch_data[lidx_str]>=gap_win)
    atr = dh.ATR(xdf, chan)
    donch_data['prevhh'] = donch_data[hh_str].shift(1)
    donch_data['prevll'] = donch_data[ll_str].shift(1)
    xdata = pd.concat([donch_data[hidx_str], donch_data[hh_str],
                       donch_data[lidx_str], donch_data[ll_str],
                       xdf['ssetup'], xdf['bsetup'],atr,
                       donch_data[hh_str].shift(1), donch_data[ll_str].shift(1)],
                       axis=1, keys=['hh_idx', 'hh', 'll_idx', 'll', 'ssetup', 'bsetup', 'ATR', 'prev_hh', 'prev_ll']).fillna(0)
    xdata = xdata.shift(1)
    mdf = mdf.join(xdata, how = 'left').fillna(method='ffill')
    mdf['pos'] = pd.Series([0]*ll, index = mdf.index)
    mdf['cost'] = pd.Series([0]*ll, index = mdf.index)
    curr_pos = []
    closed_trades = []
    end_d = mdf.index[-1].date
    #prev_d = start_d - datetime.timedelta(days=1)
    tradeid = 0
    for idx, dd in enumerate(mdf.index):
        mslice = mdf.ix[dd]
        min_id = mslice.min_id
        min_cnt = (min_id-300)/100 * 60 + min_id % 100 + 1
        if len(curr_pos) == 0:
            pos = 0
        else:
            pos = curr_pos[0].pos
        mdf.ix[dd, 'pos'] = pos
        if (mslice.prev_hh == 0):
            continue
        if (min_id >= config['exit_min']) and (close_daily or (mslice.datetime.date == end_d)):
            if (pos != 0):
                curr_pos[0].close(mslice.close - misc.sign(pos) * offset , dd)
                tradeid += 1
                curr_pos[0].exit_tradeid = tradeid
                closed_trades.append(curr_pos[0])
                curr_pos = []
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost) 
                pos = 0
        elif min_id not in no_trade_set:
            if (pos!=0):
                exit_flag = False
                if ((pos > 0) and (mslice.close <= mslice.exit_ll)) or ((pos < 0) and (mslice.close >= mslice.exit_hh)):
                    exit_flag = True
                if exit_flag or curr_pos[0].check_exit( mslice.close, 0):
                    curr_pos[0].close(mslice.close-offset*misc.sign(pos), dd)
                    tradeid += 1
                    curr_pos[0].exit_tradeid = tradeid
                    closed_trades.append(curr_pos[0])
                    curr_pos = []
                    mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)    
                    pos = 0
                elif pos_update and (min_cnt % config['pos_freq'] == 0):
                    curr_pos[0].update_price(mslice.close)
            if mslice.bsetup and (pos == 0) and (mslice.close>=mslice.prev_ll):
                new_pos = pos_class([mslice.contract], [1], unit, mslice.close + offset, mslice.low, **pos_args)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close + offset, dd)
                curr_pos.append(new_pos)
                pos = unit
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
            elif mslice.ssetup and (pos == 0) and mslice.close<=mslice.prev_hh:
                new_pos = pos_class([mslice.contract], [1], -unit, mslice.close - offset, mslice.high, **pos_args)
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

def gen_config_file(filename):
    sim_config = {}
    sim_config['sim_func']  = 'bktest_ttl_soup.ttl_soup_sim'
    sim_config['scen_keys'] = ['gap_win', 'stoploss']
    sim_config['sim_name']   = 'ttlsoup_test'
    sim_config['products']   = [ 'm', 'RM', 'y', 'p', 'a', 'rb', 'SR', 'TA', 'MA', 'i', 'ru', 'j', 'jm', 'jd', 'l', 'pp', 'v', 'cu']
    sim_config['start_date'] = '20131101'
    sim_config['end_date']   = '20151118'
    #sim_config['freq']  =  [ '15m', '60m' ]
    sim_config['pos_class'] = 'strat.ParSARTradePos'
    sim_config['proc_func'] = 'dh.day_split'#'min_freq_group'
    #chan_func = {'high': {'func': 'dh.DONCH_H', 'args':{}},
    #             'low':  {'func': 'dh.DONCH_L', 'args':{}},
    #             }
    sim_config['gap_win'] = [2, 3, 4]
    sim_config['stoploss'] = [1, 2, 3]
    config = {'capital': 10000,
              'offset': 0,
              'chan': 20,
              'exit_ratio': 0.3,
              'trans_cost': 0.0,
              'close_daily': False,
              'unit': 1,
              'stoploss': 2,
              'proc_args': {'minlist':[]},
              #'proc_args': {'freq':15},
              'pos_args': { 'af': 0.02, 'incr': 0.02, 'cap': 0.2},
              'pos_update': True,
              'pos_freq':15,
              }
    sim_config['config'] = config
    with open(filename, 'w') as outfile:
        json.dump(sim_config, outfile)
    return sim_config

if __name__=="__main__":
    args = sys.argv[1:]
    if len(args) < 1:
        print "need to input a file name for config file"
    else:
        gen_config_file(args[0])
    pass
