import datetime
import os
import sys
import json
import pandas as pd
import numpy as np
import data_handler as dh
import strategy as strat
import misc
import platform

sim_margin_dict = { 'au': 0.06, 'ag': 0.08, 'cu': 0.07, 'al':0.05,
                'zn': 0.06, 'rb': 0.06, 'ru': 0.12, 'a': 0.05,
                'm':  0.05, 'RM': 0.05, 'y' : 0.05, 'p': 0.05,
                'c':  0.05, 'CF': 0.05, 'i' : 0.05, 'j': 0.05,
                'jm': 0.05, 'pp': 0.05, 'l' : 0.05, 'SR': 0.06,
                'TA': 0.06, 'TC': 0.05, 'ME': 0.06, 'IF': 0.1,
                'jd': 0.06, 'ni': 0.07, 'IC': 0.1,
                'IH': 0.01, 'FG': 0.05, 'TF':0.015, 'OI': 0.05,
                'T': 0.015, 'MA': 0.06, 'cs': 0.05, 'bu': 0.07, 
                'sn': 0.05, 'v': 0.05 }
sim_start_dict = { 'c': datetime.date(2008,10,1), 'm': datetime.date(2010,10,1),
    'y': datetime.date(2010,10,1), 'l': datetime.date(2010,10,1), 'rb':datetime.date(2010,10,1),
    'p': datetime.date(2010,10,1), 'cu':datetime.date(2010,10,1), 'al':datetime.date(2010,10,1),
    'zn':datetime.date(2010,10,1), 'au':datetime.date(2010,10,1), 'v': datetime.date(2010,10,1),
    'a': datetime.date(2010,10,1), 'ru':datetime.date(2010,10,1), 'ag':datetime.date(2012,7,1),
    'i': datetime.date(2013,11,26), 'j': datetime.date(2011,6,1), 'jm':datetime.date(2013,5,1),
    'ME':datetime.date(2012,2,1),  'CF':datetime.date(2012,6,1),  'TA':datetime.date(2012,6,1),
    'PM':datetime.date(2012,10,1), 'RM':datetime.date(2013,2,1),  'SR':datetime.date(2013,2,1),
    'FG':datetime.date(2013,2,1),  'OI':datetime.date(2013,6,1),  'RI':datetime.date(2013,6,1),
    'TC':datetime.date(2013,10,1), 'WH':datetime.date(2014,2,1),  'pp':datetime.date(2014,4,1),
    'IF':datetime.date(2010,7,1),  'MA':datetime.date(2015,7,1),  'TF':datetime.date(2014,4,1),
    'IH':datetime.date(2015,5,1),  'IC':datetime.date(2015,5,1),  'cs':datetime.date(2015,2,2),
    'jd':datetime.date(2014,6,1),  'ni':datetime.date(2015,6,1),  'sn':datetime.date(2015,6,1),
    }

def get_bktest_folder():
    folder = ''
    system = platform.system()
    if system == 'Linux':
        folder = '/home/harvey/dev/pyctp2/results/'
    elif system == 'Windows':
        folder = 'C:\\dev\\pyktlib\\pyktrader\\results\\'
    return folder
    
def get_asset_tradehrs(asset):
    exch = 'SHFE'
    for ex in misc.product_code:
        if asset in misc.product_code[ex]:
            exch = ex
            break
    hrs = [(1500, 1615), (1630, 1730), (1930, 2100)]
    if exch in ['SSE', 'SZE']:
        hrs = [(1530, 1730), (1900, 2100)]
    elif exch == 'CFFEX':
        hrs = [(1515, 1730), (1900, 2115)]
    else:
        if asset in misc.night_session_markets:
            night_idx = misc.night_session_markets[asset]
            hrs = [misc.night_trading_hrs[night_idx]] + hrs
    return hrs
    
def cleanup_mindata(df, asset):
    cond = None
    tradehrs = get_asset_tradehrs(asset)
    for idx, hrs in enumerate(tradehrs):
        if idx == 0:
            cond = (df.min_id>= tradehrs[idx][0]) & (df.min_id < tradehrs[idx][1])
        else:
            cond = cond | (df.min_id>= tradehrs[idx][0]) & (df.min_id < tradehrs[idx][1])
    df = df.ix[cond]
    df = df[(df.close > 0) & (df.high > 0) & (df.open > 0) & (df.low > 0)]
    return df

def get_pnl_stats(df, start_capital, marginrate, freq):
    df['pnl'] = df['pos'].shift(1)*(df['close'] - df['close'].shift(1)).fillna(0.0)
    df['margin'] = pd.concat([df.pos*marginrate[0]*df.close, -df.pos*marginrate[1]*df.close], join='outer', axis=1).max(1)
    if freq == 'm':
        daily_pnl = pd.Series(df['pnl']).resample('1d',how='sum').dropna()
        daily_margin = pd.Series(df['margin']).resample('1d',how='last').dropna()
        daily_cost = pd.Series(df['cost']).resample('1d',how='sum').dropna()
    else:
        daily_pnl = pd.Series(df['pnl'])
        daily_margin = pd.Series(df['margin'])
        daily_cost = pd.Series(df['cost'])
    daily_pnl.name = 'daily_pnl'
    daily_margin.name = 'daily_margin'
    daily_cost.name = 'daily_cost'
    cum_pnl = pd.Series(daily_pnl.cumsum() + daily_cost.cumsum() + start_capital, name = 'cum_pnl')
    available = cum_pnl - daily_margin
    res = {}
    res['avg_pnl'] = daily_pnl.mean()
    res['std_pnl'] = daily_pnl.std()
    res['tot_pnl'] = daily_pnl.sum()
    res['tot_cost'] = daily_cost.sum()
    res['num_days'] = len(daily_pnl)
    res['sharp_ratio'] = res['avg_pnl']/res['std_pnl']*np.sqrt(252.0)
    max_dd, max_dur = max_drawdown(cum_pnl)
    res['max_margin'] = daily_margin.max()
    res['min_avail'] = available.min() 
    res['max_drawdown'] =  max_dd
    res['max_dd_period'] =  max_dur
    if abs(max_dd) > 0:
        res['profit_dd_ratio'] = res['tot_pnl']/abs(max_dd)
    else:
        res['profit_dd_ratio'] = 0
    ts = pd.concat([cum_pnl, daily_margin, daily_cost], join='outer', axis=1)
    return res, ts

def get_trade_stats(trade_list):
    res = {}
    res['n_trades'] = len(trade_list)
    res['all_profit'] = sum([trade.profit for trade in trade_list])
    res['win_profit'] = sum([trade.profit for trade in trade_list if trade.profit>0])
    res['loss_profit'] = sum([trade.profit for trade in trade_list if trade.profit<0])
    sorted_profit = sorted([trade.profit for trade in trade_list])
    res['largest_profit'] = sorted_profit[-1]
    res['second largest'] = sorted_profit[-2]
    res['third_profit'] = sorted_profit[-3]
    res['largest_loss'] = sorted_profit[0]
    res['second_loss'] = sorted_profit[1]
    res['third_loss'] = sorted_profit[2]
    res['num_win'] = len([trade.profit for trade in trade_list if trade.profit>0])
    res['num_loss'] = len([trade.profit for trade in trade_list if trade.profit<0])
    res['win_ratio'] = 0
    if res['n_trades'] > 0:
        res['win_ratio'] = float(res['num_win'])/float(res['n_trades'])
    res['profit_per_win'] = 0
    if res['num_win'] > 0:
        res['profit_per_win'] = res['win_profit']/float(res['num_win'])
    res['profit_per_loss'] = 0
    if res['num_loss'] > 0:    
        res['profit_per_loss'] = res['loss_profit']/float(res['num_loss'])
    
    return res

def create_drawdowns(ts):
    """
    Calculate the largest peak-to-trough drawdown of the PnL curve
    as well as the duration of the drawdown. Requires that the 
    pnl_returns is a pandas Series.
    Parameters:
    pnl - A pandas Series representing period percentage returns.
    Returns:
    drawdown, duration - Highest peak-to-trough drawdown and duration.
    """

    # Calculate the cumulative returns curve 
    # and set up the High Water Mark
    # Then create the drawdown and duration series
    ts_idx = ts.index
    drawdown = pd.Series(index = ts_idx)
    duration = pd.Series(index = ts_idx)
    hwm = pd.Series([0]*len(ts), index = ts_idx)
    last_t = ts_idx[0]
    # Loop over the index range
    for idx, t in enumerate(ts_idx):
        if idx > 0:
            cur_hwm = max(hwm[last_t], ts_idx[idx])
            hwm[t] = cur_hwm
            drawdown[t]= hwm[t] - ts[t]
            duration[t]= 0 if drawdown[t] == 0 else duration[last_t] + 1
        last_t = t
    return drawdown.max(), duration.max()

def max_drawdown(ts):
    i = np.argmax(np.maximum.accumulate(ts)-ts)
    j = np.argmax(ts[:i])
    max_dd = ts[i] - ts[j]
    max_duration = (i - j).days
    return max_dd, max_duration

def simlauncher_min(config_file):
    sim_config = {}
    with open(config_file, 'r') as fp:
        sim_config = json.load(fp)
    bktest_split = sim_config['sim_func'].split('.')
    bktest_module = __import__(bktest_split[0])
    run_sim = getattr(bktest_module, bktest_split[1])
    dir_name = config_file.split('.')[0]
    test_folder = get_bktest_folder()
    file_prefix = test_folder + dir_name + os.path.sep
    if not os.path.exists(file_prefix):
        os.makedirs(file_prefix)
    sim_list = sim_config['products']
    config = {}
    start_date = datetime.datetime.strptime(sim_config['start_date'], '%Y%m%d').date()
    config['start_date'] = start_date
    end_date   = datetime.datetime.strptime(sim_config['end_date'], '%Y%m%d').date()
    config['end_date'] = end_date
    scen_dim = [ len(sim_config[s]) for s in sim_config['scen_keys']]
    scenarios = [list(s) for s in np.ndindex(tuple(scen_dim))]
    config.update(sim_config['config'])
    config['pos_class'] = eval(sim_config['pos_class'])
    config['proc_func'] = eval(sim_config['proc_func'])
    file_prefix = file_prefix + sim_config['sim_name']
    if config['close_daily']:
        file_prefix = file_prefix + 'daily_'
    config['file_prefix'] = file_prefix
    for asset in sim_list:
        file_prefix = config['file_prefix'] + '_' + asset + '_'
        fname = file_prefix + 'stats.json'
        output = {}
        if os.path.isfile(fname):
            with open(fname, 'r') as fp:
                output = json.load(fp)
        if len(output.keys()) >= len(scenarios):
            continue
        if asset in sim_start_dict:
            start_date =  max(sim_start_dict[asset], config['start_date'])
        else:
            start_date = config['start_date']
        config['marginrate'] = ( sim_margin_dict[asset], sim_margin_dict[asset])
        config['nearby'] = 1
        config['rollrule'] = '-50b'
        config['exit_min'] = 2112
        config['no_trade_set'] = range(300, 301) + range(1500, 1501) + range(2059, 2100)
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
        config['no_trade_set'] = []
        nearby   = config['nearby']
        rollrule = config['rollrule']
        if nearby > 0:
            mdf = misc.nearby(asset, nearby, start_date, end_date, rollrule, 'm', need_shift=True)
        mdf = cleanup_mindata(mdf, asset)
        if 'need_daily' in sim_config:
            ddf = misc.nearby(asset, nearby, start_date, end_date, rollrule, 'd', need_shift=True)
            config['ddf'] = ddf
        for ix, s in enumerate(scenarios):
            fname1 = file_prefix + str(ix) + '_trades.csv'
            fname2 = file_prefix + str(ix) + '_dailydata.csv'
            if os.path.isfile(fname1) and os.path.isfile(fname2):
                continue
            for key, seq in zip(sim_config['scen_keys'], s):
                config[key] = sim_config[key][seq]
            df = mdf.copy(deep = True)
            (res, closed_trades, ts) = run_sim( df, config)
            output[ix] = res
            print 'saving results for asset = %s, scen = %s' % (asset, str(ix))
            all_trades = {}
            for i, tradepos in enumerate(closed_trades):
                all_trades[i] = strat.tradepos2dict(tradepos)
            trades = pd.DataFrame.from_dict(all_trades).T
            trades.to_csv(fname1)
            ts.to_csv(fname2)
            fname = file_prefix + 'stats.json'
            try:
                with open(fname, 'w') as ofile:
                    json.dump(output, ofile)
            except:
                continue
        #res = pd.DataFrame.from_dict(output)
    return

if __name__=="__main__":
    args = sys.argv[1:]
    if len(args) < 1:
        print "need to input a file name for simulation"
    else:
        simlauncher_min(args[0])
    pass