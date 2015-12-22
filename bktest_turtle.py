import misc
import json
import data_handler as dh
import pandas as pd
import numpy as np
import strategy as strat
import sys
import backtest

def turtle_sim( mdf, config ):
	ddf = config['ddf']
    marginrate = config['marginrate']
    offset = config['offset']a
    start_equity = config['capital']
    tcost = config['trans_cost']
    signals = config['chan']
    unit = config['unit']
    param = config['param']
	max_pos = param[1]
	max_loss = param[0]
    ma_ratio = config['ma_ratio']
	use_ma = config['use_ma']
	chan_func = config['chan_func']
    ddf['ATR'] =dh.ATR(ddf, n=chan[0]).shift(1))
    ddf['OL_1'] = eval(chan_func['high']['func'])(ddf, chan[0]).shift(1)
    ddf['OS_1'] = eval(chan_func['low']['func'])(ddf, chan[0]).shift(1)
    ddf['CL_1'] = eval(chan_func['low']['func'])(ddf, chan[1]).shift(1)
    ddf['CS_1'] = eval(chan_func['high']['func'])(ddf, chan[1]).shift(1)
    ddf['MA1'] = dh.MA(ddf, ma_ratio*chan[0]).shift(1)
    ddf['MA2'] = dh.MA(ddf, chan[1]).shift(1)
    ll = mdf.shape[0]
    mdf['pos'] = pd.Series([0]*ll, index = mdf.index)
    mdf['cost'] = pd.Series([0]*ll, index = mdf.index)
    curr_pos = []
    tradeid = 0
    closed_trades = []
	end_d = mdf.index[-1].date()
    curr_atr = 0
    for idx, dd in enumerate(mdf.index):
        mslice = mdf.ix[dd]
        d = dd.date()
        dslice = ddf.ix[d]
        tot_pos = sum( [trade.pos for trade in curr_pos] ) 
        mdf.ix[dd, 'pos'] = tot_pos
        if np.isnan(dslice.ATR):
            continue
        if (min_id >= config['exit_min']) :
            if (tot_pos != 0) and (d == end_d):
                for trade_pos in curr_pos:
                    trade_pos.close(mslice.close - misc.sign(trade_pos.pos) * offset, dd)
                    tradeid += 1
                    trade_pos.exit_tradeid = tradeid
                    closed_trades.append(trade_pos)
                    mdf.ix[dd, 'cost'] -= abs(trade_pos.pos) * (offset + mslice.close*tcost)
                curr_pos = []
				tot_pos = 0
        elif min_id not in no_trade_set:
			if tot_pos == 0:
				curr_atr = dslice.ATR
				direction = 0
				dol = dslice.OL_1
				dos = dslice.OS_1
				if use_MA:
					dol = max(dol, dslice.MA)
					dos = min(dos, dslice.MA)        
				if (mslice.close >= dol) and ((use_ma == False) or (mslice.MA1 >= mslice.MA2)):
					direction = 1
				elif (mslice.close <= dos) and ((use_ma == False) or (mslice.MA1 <= mslice.MA2)):
					direction = -1
				pos = direction * unit
				if direction != 0:
					new_pos = strat.TradePos([mslice.contract], [1], pos, mslice.close, mslice.close)
					tradeid += 1
					new_pos.entry_tradeid = tradeid
					new_pos.open(mslice.close + direction * offset, dd)
					mdf.ix[dd, 'cost'] -= abs(pos) * (offset + mslice.close*tcost)
					curr_pos.append(new_pos)
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
				elif curr_pos[-1].check_exit( mslice.close, curr_atr * max_loss ):
					for trade_pos in curr_pos:
						if trade_pos.check_exit( mslice.close, curr_atr * max_loss ):
							trade_pos.close(mslice.close - misc.sign(trade_pos.pos) * offset, dd)
							tradeid += 1
							trade_pos.exit_tradeid = tradeid
							closed_trades.append(trade_pos)
							mdf.ix[dd, 'cost'] -= abs(trade_pos.pos) * (offset + mslice.close*tcost)
					curr_pos = [trade for trade in curr_pos if not trade.is_closed]
				#add positions
				elif (len(curr_pos) < max_pos) and (mslice.close - curr_pos[-1].entry_price)*direction > curr_atr/max_pos*max_loss:
					for trade_pos in curr_pos:
						#trade.exit_target += curr_atr/max_pos*max_loss * direction
						trade_pos.set_exit( mslice.close )
					new_pos = strat.TradePos([mslice.contract], [1], direction*unit, mslice.close, mslice.close)
					tradeid += 1
					new_pos.entry_tradeid = tradeid
					new_pos.open(mslice.close + direction * offset, dd)
					mdf.ix[dd, 'cost'] -= abs(pos) * (offset + mslice.close*tcost)
					curr_pos.append(new_pos)
				if (len(curr_pos) > 0) and pos_update:
					for trade_pos in curr_pos:
						trade_pos.update_price(mslice.close)
        mdf.ix[dd, 'pos'] = sum( [trade.pos for trade in curr_pos] )    

    (res_pnl, ts) = backtest.get_pnl_stats( mdf, start_equity, marginrate, 'm')
    res_trade = backtest.get_trade_stats( closed_trades )
    res = dict( res_pnl.items() + res_trade.items())
    return (res, closed_trades, ts)

def gen_config_file(filename):
    sim_config = {}
    sim_config['sim_func']  = 'bktest_turtle.turtle_sim'
    sim_config['scen_keys'] = ['chan', 'param']
    sim_config['sim_name']   = 'Turtle_'
    sim_config['products']   = ['m', 'RM', 'y', 'p', 'l', 'pp', 'a', 'rb', 'SR', 'TA', 'MA', 'i', 'ru', 'j', 'jd', 'jm', 'ag', 'cu','TF', 'IF', 'ME']
    sim_config['start_date'] = '20121101'
    sim_config['end_date']   = '20151118'
    sim_config['need_daily'] = True
    sim_config['chan']  = [(10, 3), (10, 5), (15, 5), (20, 5), (20, 10)]
	sim_config['param'] = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (2, 4)]
    sim_config['pos_class'] = 'strat.TradePos'
    #sim_config['proc_func'] = 'dh.day_split'
    sim_config['offset']    = 1
    #chan_func = { 'high': {'func': 'dh.PCT_CHANNEL', 'args':{'pct': 90, 'field': 'high'}},
    #              'low':  {'func': 'dh.PCT_CHANNEL', 'args':{'pct': 10, 'field': 'low'}}}
    chan_func = { 'high': {'func': 'dh.DONCH_H', 'args':{}},
                  'low':  {'func': 'dh.DONCH_L', 'args':{}}}
    
	config = {'capital': 10000,
              'trans_cost': 0.0,
              'close_daily': False,
              'unit': 1,
              'pos_args': {},
              'chan_func': chan_func,
			  'ma_ratio': 2,
			  'use_ma': False,
			  'pos_update': False,
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
