import misc
import data_handler as dh
import pandas as pd
import numpy as np
import strategy as strat
import datetime
import openpyxl
import os
import backtest

def dual_thrust_sim( asset, start_date, end_date, nearby=1, rollrule='-20b', k_buy = 1.0, k_sell = 1.0 ):
    ddf = misc.nearby(asset, nearby, start_date, end_date, rollrule, need_shift=True)
    mdf = misc.nearby(asset, nearby, start_date, end_date, rollrule, need_shift=True)
    res[cont] = {}
    ddf['TR'] = pd.concat([ddf['high']-ddf['close'], ddf['close']-ddf['low']], join='outer', axis=1).max(axis=1).shift(1) 
    ll = mdf.shape[0]
    mdf['pos'] = pd.Series([0]*ll, index = mdf.index)
    curr_pos = []
    closed_trades = []
	start_d = ddf.index[0]
	prev_d = start_d - datetime.timedelta(days=1)
    tradeid = 0
    for idx, dd in enumerate(mdf.index):
        mslice = mdf.ix[dd]
        d = dd.date()
        dslice = ddf.ix[d]
        if d < start_d + datetime.timedelta(days=1):
            continue
		d_open = dslice.open
		if (d.open == 0):
			if (prev_d < d):
				d_open = mslice.open
		else:
			d_open = dslice.open
		prev_d = d
		buytrig  = dslice.open + dslice.TR * k_buy
		selltrig = dslice.open - dslice.TR * k_sell
        if len(curr_pos) == 0:
            pos = 0
        else:
            pos = curr_pos[0].pos
		if (mslice.close >= buytrig) and (pos <=0 ):
            if len(curr_pos) > 0:
                curr_pos[0].close(mslice.close, dd)



                if len(curr_pos) == 0 and idx < len(mdf.index)-NO_OPEN_POS_PROTECT:
                    direction = 0
                    if mslice.close > dslice.OL_1:
                        #n_unit = min(max(int((u.close - u.OL_1)*2.0/u.ATR_20 + 1),0),4)
                        direction = 1
                    elif mslice.close < dslice.OS_1:
                        #n_unit = min(max(int((u.OS_1 - u.low) *2.0/u.ATR_20 + 1),0),4)
                        direction = -1
                    mdf.ix[dd, 'pos'] = direction
                    if direction != 0:
                        trade = strat.TradePos([cont], [1], direction, mslice.close, mslice.close- direction * dslice.ATR_20 * NN)
                        tradeid += 1
                        trade.open(mslice.close, dd, tradeid)
                        curr_pos.append(trade)
                        atr_dict[cont] = dslice.ATR_20
                elif (idx >= len(mdf.index)-NO_OPEN_POS_PROTECT):
                    if len(curr_pos)>0:
                        for trade in curr_pos:
                            trade.close( mslice.close, dd, trade.entry_tradeid)
                            closed_trades.append(trade)
                        curr_pos = []
                else:
                    direction = curr_pos[0].direction
                    tot_pos = sum([trade.pos * trade.direction for trade in curr_pos])
                    #exit position out of channel
                    if (direction == 1 and mslice.close < dslice.CL_1) or \
                            (direction == -1 and mslice.close > dslice.CS_1):
                        for trade in curr_pos:
                            trade.close( mslice.close, dd, trade.entry_tradeid )
                            closed_trades.append(trade)
                        curr_pos = []
                    #stop loss position partially
                    elif (curr_pos[-1].exit_target - mslice.close) * direction >= 0:
                        for trade in curr_pos:
                            if (trade.exit_target - mslice.close) * direction > 0:
                                trade.close(mslice.close, dd, trade.entry_tradeid)
                                closed_trades.append(trade)
                        curr_pos = [trade for trade in curr_pos if not trade.is_closed]
                    #add positions
                    elif (tot_pos < 4) and (mslice.close - curr_pos[-1].entry_price)*direction > atr_dict[cont]/2.0:
                        for trade in curr_pos:
                            trade.exit_target += atr_dict[cont]/2.0*direction
                        trade = strat.TradePos([cont], [1], direction, mslice.close, mslice.close - direction * atr_dict[cont] * NN)
                        tradeid += 1
                        trade.open(mslice.close, dd, tradeid)
                        curr_pos.append(trade)
                    mdf.ix[dd, 'pos'] = sum( [trade.pos for trade in curr_pos] )    
            mdf['pnl'] = mdf['pos'].shift(1)*(mdf['close'] - mdf['close'].shift(1))
            mdf['cum_pnl'] = mdf['pnl'].cumsum()
            #max_dd, max_dur = backtest.max_drawdown(mdf['cum_pnl'])
            #drawdown_j = np.argmax(mdf['cum_pnl'][:drawdown_i])
            daily_pnl = pd.Series(mdf['pnl']).resample('1d',how='sum').dropna()
            daily_pnl.name = 'dailyPNL'
            if len(daily_pnl) < 5:
                continue
            cum_pnl = daily_pnl.cumsum()
            res[cont]['avg_pnl'] = daily_pnl.mean()
            res[cont]['std_pnl'] = daily_pnl.std()
            res[cont]['tot_pnl'] = daily_pnl.sum()
            res[cont]['num_days'] = len(daily_pnl)
            res[cont]['sharp_ratio'] = res[cont]['avg_pnl']/res[cont]['std_pnl']*np.sqrt(252.0)
            max_dd, max_dur = backtest.max_drawdown(cum_pnl)
            res[cont]['max_drawdown'] =  max_dd
            res[cont]['max_dd_period'] =  max_dur
            res[cont]['n_trades'] = len(closed_trades)
            res[cont]['all_profit'] = sum([trade.profit for trade in closed_trades])
            if abs(max_dd) > 0:
                res[cont]['profit_dd_ratio'] = res[cont]['all_profit']/abs(max_dd)
            else:
                res[cont]['profit_dd_ratio'] = 0
            res[cont]['win_profit'] = sum([trade.profit for trade in closed_trades if trade.profit>0])
            res[cont]['loss_profit'] = sum([trade.profit for trade in closed_trades if trade.profit<0])
            res[cont]['num_win'] = len([trade.profit for trade in closed_trades if trade.profit>0])
            res[cont]['num_loss'] = len([trade.profit for trade in closed_trades if trade.profit<0])
            res[cont]['win_ratio'] = 0
            if res[cont]['n_trades'] > 0:
                res[cont]['win_ratio'] = float(res[cont]['num_win'])/float(res[cont]['n_trades'])
            res[cont]['profit_per_win'] = 0
            if res[cont]['num_win'] > 0:
                res[cont]['profit_per_win'] = res[cont]['win_profit']/float(res[cont]['num_win'])
            res[cont]['profit_per_loss'] = 0
            if res[cont]['num_loss'] > 0:    
                res[cont]['profit_per_loss'] = res[cont]['loss_profit']/float(res[cont]['num_loss'])
            ntrades = len(all_trades)
            for i, tradepos in enumerate(closed_trades):
                all_trades[ntrades+i] = strat.tradepos2dict(tradepos)
        results[pc] = pd.DataFrame.from_dict(res)
        trades[pc] = pd.DataFrame.from_dict(all_trades).T    
    return (results, trades)

def save_sim_results(file_prefix, res, trades):
    for pc in res:
        df = res[pc]
        fname = file_prefix+'_'+ pc +'_stats.csv'
        df.to_csv(fname)
        df = trades[pc]
        fname = file_prefix+'_'+ pc +'_trades.csv'
        df.to_csv(fname)
    return
    
if __name__=="__main__":
    rollrule = '-30b'
    commod_list1= ['m','y','a','p','v','l','ru','rb','au','cu','al','zn','ag','i','j','jm'] #
    start_dates1 = [datetime.date(2010,9,1)] * 9 + [datetime.date(2010,10,1)] * 3 + \
                [datetime.date(2012,7,1), datetime.date(2014,1,2), datetime.date(2011,6,1),datetime.date(2013,5,1)]
    commod_list2 = ['ME', 'CF', 'TA', 'PM', 'RM', 'SR', 'FG', 'OI', 'RI', 'TC', 'WH']
    start_dates2 = [datetime.date(2012, 2,1)] + [ datetime.date(2012, 6, 1)] * 2 + [datetime.date(2012, 10, 1)] + \
                [datetime.date(2013, 2, 1)] * 3 + [datetime.date(2013,6,1)] * 2 + [datetime.date(2013, 10, 1), datetime.date(2014,2,1)]
    commod_list = commod_list1+commod_list2
    start_dates = start_dates1 + start_dates2
    end_date = datetime.date(2014,11,7)
    systems = [[20,10],[15,7],[40,20],[55,20]]
    for sys in systems:
        file_prefix = 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\results\\turtle_R20b_%s' % sys[0]
        for cmd,sdate in zip(commod_list, start_dates):
            nearby = 1
            if cmd in ['cu','al','zn']:
                nearby = 2
                continue
            (res, trades) = turtle_sim( [cmd], sdate, end_date, nearby = nearby, rollrule = rollrule, signals = sys )
            print 'saving results for cmd = %s, sys= %s' % (cmd, sys[0])
            save_sim_results(file_prefix, res, trades)
            
            
