import misc
import data_handler as dh
import pandas as pd
import numpy as np
import backtest as sim
import datetime
import openpyxl
import os

def simtrade2dict(simtrade):
    trade = {}
    trade['instID'] = simtrade.inst
    trade['pos'] = simtrade.pos
    trade['direction'] = simtrade.direction
    trade['price_in'] = simtrade.price_in
    trade['exit'] = simtrade.exit
    trade['start_time'] = simtrade.start_time
    trade['profit'] = simtrade.profit
    trade['end_time'] = simtrade.end_time
    trade['price_out'] = simtrade.price_out
    trade['is_closed'] = simtrade.is_closed
    return trade
    
def turtle_sim( assets, start_date, end_date, nearby=1, rollrule='-20b', signals = [20,10] ):
    NN = 2
    histdays = '-' + str(signals[0]+5) + 'd'
    NO_OPEN_POS_PROTECT = 30
    start_idx = 0
    ddata = {}
    mdata = {}
    results = {}
    trades = {}
    atr_dict = {}
    for pc in assets:
        ddata[pc] = misc.rolling_hist_data(pc, nearby, start_date, end_date, rollrule, 'd', histdays)
        mdata[pc] = misc.rolling_hist_data(pc, nearby, start_date, end_date, rollrule, 'm', '-1b')
        res = {}
        all_trades = {}
        for i in range(len(ddata[pc])):
            ddf = ddata[pc][i]['data']
            mdf = mdata[pc][i]['data']
            cont = ddata[pc][i]['contract']
            res[cont] = {}
#             ts = dh.ATR(ddf, n=20)
#             ddf = ddf.join(ts)
#             ts = dh.DONCH_H(ddf, 55)
#             ddf = ddf.join(ts)
#             ts = dh.DONCH_L(ddf, 55)
#             ddf = ddf.join(ts)
#             ts = dh.DONCH_H(ddf, 20)
#             ddf = ddf.join(ts)
#             ts = dh.DONCH_L(ddf, 20)
            ddf['ATR_20'] = pd.Series(dh.ATR(ddf, n=20).shift(1))
            ddf['OL_1'] = pd.Series(dh.DONCH_H(ddf, signals[0]).shift(1))
            ddf['OS_1'] = pd.Series(dh.DONCH_L(ddf, signals[0]).shift(1))
            ddf['CL_1'] = pd.Series(dh.DONCH_L(ddf, signals[1]).shift(1))
            ddf['CS_1'] = pd.Series(dh.DONCH_H(ddf, signals[1]).shift(1))
            #df['OL_2'] = pd.concat([df.DONCH_H55.shift(1), df.open], join='outer', axis=1).max(axis=1)
            #df['OS_2'] = pd.concat([df.DONCH_L55.shift(1), df.open], join='outer', axis=1).min(axis=1)
            #df['CL_2'] = pd.concat([df.DONCH_L20.shift(1), df.open], join='outer', axis=1).min(axis=1)
            #df['CS_2'] = pd.concat([df.DONCH_H20.shift(1), df.open], join='outer', axis=1).max(axis=1)
            ll = mdf.shape[0]
            mdf['pos'] = pd.Series([0]*ll, index = mdf.index)
            curr_pos = []
            closed_trades = []
            for idx, dd in enumerate(mdf.index):
                mslice = mdf.ix[dd]
                d = dd.date()
                dslice = ddf.ix[d]
                if idx < start_idx:
                    continue
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
                        trade = sim.SimTrade(cont, mslice.close, direction, mslice.close- direction * dslice.ATR_20 * NN, dd)
                        curr_pos.append(trade)
                        atr_dict[cont] = dslice.ATR_20
                elif (idx >= len(mdf.index)-NO_OPEN_POS_PROTECT):
                    if len(curr_pos)>0:
                        for trade in curr_pos:
                            trade.close( mslice.close, dd )
                            closed_trades.append(trade)
                        curr_pos = []
                else:
                    direction = curr_pos[0].direction
                    tot_pos = sum([trade.pos * trade.direction for trade in curr_pos])
                    #exit position out of channel
                    if (direction == 1 and mslice.close < dslice.CL_1) or \
                            (direction == -1 and mslice.close > dslice.CS_1):
                        for trade in curr_pos:
                            trade.close( mslice.close, dd )
                            closed_trades.append(trade)
                        curr_pos = []
                    #stop loss position partially
                    elif (curr_pos[-1].exit - mslice.close) * direction >= 0:
                        for trade in curr_pos:
                            if (trade.exit - mslice.close) * direction > 0:
                                trade.close(mslice.close, dd)
                                closed_trades.append(trade)
                        curr_pos = [trade for trade in curr_pos if not trade.is_closed]
                    #add positions
                    elif (tot_pos < 4) and (mslice.close - curr_pos[-1].price_in)*direction > atr_dict[cont]/2.0:
                        for trade in curr_pos:
                            trade.exit += atr_dict[cont]/2.0*direction
                        trade = sim.SimTrade(cont, mslice.close, direction, mslice.close - direction * atr_dict[cont] * NN, dd)
                        curr_pos.append(trade)
                    mdf.ix[dd, 'pos'] = sum( [trade.pos for trade in curr_pos] )    
            mdf['pnl'] = mdf['pos'].shift(1)*(mdf['close'] - mdf['close'].shift(1))
            mdf['cum_pnl'] = mdf['pnl'].cumsum()
            #drawdown_i = np.argmax(np.maximum.accumulate(mdf['cum_pnl']) - mdf['cum_pnl'])
            #drawdown_j = np.argmax(mdf['cum_pnl'][:drawdown_i])
            daily_pnl = pd.Series(mdf['pnl']).resample('1d',how='sum')
            daily_pnl.name = 'dailyPNL'
            res[cont]['avg_pnl'] = daily_pnl.mean()
            res[cont]['std_pnl'] = daily_pnl.std()
            res[cont]['tot_pnl'] = daily_pnl.sum()
            res[cont]['num_days'] = len(daily_pnl)
            #res[cont]['drawdown_i'] =  drawdown_i
            #res[cont]['drawdown_j'] =  drawdown_j
            res[cont]['n_trades'] = len(closed_trades)
            res[cont]['all_profit'] = sum([trade.profit for trade in closed_trades])
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
            for i, simtrade in enumerate(closed_trades):
                all_trades[ntrades+i] = simtrade2dict(simtrade)
        results[pc] = pd.DataFrame.from_dict(res)
        trades[pc] = pd.DataFrame.from_dict(all_trades).T    
    return (results, trades)

def save_sim_results(filename, res, trades):
    if os.path.isfile(filename):
        book = openpyxl.load_workbook(filename)
    xlwriter = pd.ExcelWriter(filename) 
    if os.path.isfile(filename):
        xlwriter.book = book
        xlwriter.sheets = dict((ws.title, ws) for ws in book.worksheets)
    for pc in res:
        df = res[pc]
        df.to_excel(xlwriter, pc+'_stats')
        df = trades[pc]
        df.to_excel(xlwriter, pc+'_trades')
    xlwriter.save()
    return
    
if __name__=="__main__":
    rollrule = '-20b'
    commod_list= ['m','y','a','p','v','l','ru','rb','au','cu','al','zn','ag','i','j','jm']
    start_dates = [datetime.date(2010,9,1)] * 12 + \
                [datetime.date(2012,7,1), datetime.date(2014,1,2), datetime.date(2011,6,1),datetime.date(2013,5,1)]
    end_date = datetime.date(2014,7,28)
    systems = [[20,10],[55,20],[15,5],[40,20]]
    for sys in systems:
        filename = 'C:\\dev\\src\\ktlib\\pythonctp\\pyctp\\results\\turtle_%s_R20b.xlsx' % sys[0]
        for cmd,sdate in zip(commod_list, start_dates):
            nearby = 1
            if cmd in ['cu','al','zn']:
                nearby = 2
            (res, trades) = turtle_sim( [cmd], sdate, end_date, nearby = nearby, rollrule = rollrule, signals = sys )
            print 'saving results for cmd = %s, sys= %s' % (cmd, sys[0])
            save_sim_results(filename, res, trades)
