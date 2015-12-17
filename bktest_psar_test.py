import sys
import misc
import json
import data_handler as dh
import pandas as pd
import strategy as strat
import backtest

def psar_test_sim( mdf, config):
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
    no_trade_set = config['no_trade_set']
    ll = mdf.shape[0]
    xdf = proc_func(mdf, **proc_args)
    xdf['chan_h'] = pd.rolling_max(xdf.high, chan)
    xdf['chan_l'] = pd.rolling_min(xdf.low, chan)
    xdf['MA'] = pd.rolling_mean(xdf.close, chan)
    psar_data = dh.PSAR(xdf, **config['sar_params'])
    xdata = pd.concat([xdf['MA'], xdf['chan_h'], xdf['chan_l'], psar_data['PSAR_VAL'], psar_data['PSAR_DIR'], xdf['date_idx']],
                       axis=1, keys=['MA', 'chanH', 'chanL', 'psar', 'psar_dir', 'date'])
    xdata = xdata.shift(1).fillna(0)
    mdf = mdf.join(xdata, how = 'left').fillna(method='ffill')
    mdf['pos'] = pd.Series([0]*ll, index = mdf.index)
    mdf['cost'] = pd.Series([0]*ll, index = mdf.index)
    curr_pos = []
    closed_trades = []
    end_d = mdf.index[-1].date
    #prev_d = start_d - datetime.timedelta(days=1)
    tradeid = 0
    for dd in mdf.index:
        mslice = mdf.ix[dd]
        min_id = mslice.min_id
        min_cnt = (min_id-300)/100 * 60 + min_id % 100 + 1
        if len(curr_pos) == 0:
            pos = 0
        else:
            pos = curr_pos[0].pos
        mdf.ix[dd, 'pos'] = pos
        if (mslice.MA == 0) or (mslice.chanH == 0) or (mslice.chanL == 0) or (mslice.psar_dir ==0):
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
            if (pos!=0) and pos_update:
                curr_pos[0].update_price(mslice.close)
                if (curr_pos[0].check_exit( mslice.close, SL * mslice.close )):
                    curr_pos[0].close(mslice.close-offset*misc.sign(pos), dd)
                    tradeid += 1
                    curr_pos[0].exit_tradeid = tradeid
                    closed_trades.append(curr_pos[0])
                    curr_pos = []
                    mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)    
                    pos = 0
            long_close  = ((mslice.low <= mslice.chanL) or (mslice.psar_dir < 0)) and (pos >0)
            short_close = ((mslice.high >= mslice.chanH) or (mslice.psar_dir > 0)) and (pos <0)
            close_price = mslice.close
            if (short_close or long_close):
                if (mslice.psar_dir > 0):
                    close_price = max(mslice.psar, mslice.open)
                elif (mslice.psar_dir < 0):
                    close_price = min(mslice.psar, mslice.open)
                curr_pos[0].close(mslice.close+offset, dd)
                tradeid += 1
                curr_pos[0].exit_tradeid = tradeid
                closed_trades.append(curr_pos[0])
                curr_pos = []
                pos = 0
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
            buy_trig  = (mslice.high >= mslice.chanH) and (mslice.psar_dir > 0) and (pos ==0)
            sell_trig = (mslice.low <= mslice.chanL) and (mslice.psar_dir < 0) and (pos == 0)
            if buy_trig:
                new_pos = pos_class([mslice.contract], [1], unit, mslice.close + offset, mslice.close + offset, **pos_args)
                tradeid += 1
                new_pos.entry_tradeid = tradeid
                new_pos.open(mslice.close + offset, dd)
                curr_pos.append(new_pos)
                pos = unit
                mdf.ix[dd, 'cost'] -=  abs(pos) * (offset + mslice.close*tcost)
            elif sell_trig:
                new_pos = pos_class([mslice.contract], [1], -unit, mslice.close - offset, mslice.close - offset, **pos_args)
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
    sim_config['sim_func']  = 'bktest_psar_test.psar_test_sim'
    sim_config['scen_keys'] = ['freq']
    sim_config['sim_name']   = 'psar_test'
    sim_config['products']   = ['m'] #[ 'm', 'RM', 'y', 'p', 'a', 'rb', 'SR', 'TA', 'MA', 'i', 'ru', 'j', 'jm', 'ag', 'cu', 'au', 'al', 'zn' ]
    sim_config['start_date'] = '20141101'
    sim_config['end_date']   = '20151118'
    sim_config['freq']  =  [ '15m', '60m' ]
    sim_config['pos_class'] = 'strat.TradePos'
    sim_config['proc_func'] = 'dh.min_freq_group'
    #chan_func = {'high': {'func': 'pd.rolling_max', 'args':{}},
    #             'low':  {'func': 'pd.rolling_min', 'args':{}},
    #             }
    config = {'capital': 10000,
              'offset': 0,
              'chan': 20,
              'use_chan': True,
              'sar_params': {'iaf': 0.02, 'maxaf': 0.2, 'incr': 0.02},
              'trans_cost': 0.0,
              'close_daily': True,
              'unit': 1,
              'stoploss': 0.0,
              #'proc_args': {'minlist':[1500]},
              'proc_args': {'freq':15},
              'pos_args': {},
              'pos_update': False,
              #'chan_func': chan_func,
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
