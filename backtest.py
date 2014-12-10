import datetime
import pandas as pd
import numpy as np

def get_pnl_stats(df, start_capital, marginrate, freq):
	df['pnl'] = df['pos'].shift(1)*(df['close'] - df['close'].shift(1))
	df['cum_pnl'] = df['pnl'].cumsum()
	if freq == 'm':
		daily_pnl = pd.Series(df['pnl']).resample('1d',how='sum').dropna()
	else:
		daily_pnl = pd.Series(df['pnl']).dropna()
	daily_pnl.name = 'dailyPNL'
	cum_pnl = daily_pnl.cumsum() + start_capital
	res = {}
	res['avg_pnl'] = daily_pnl.mean()
	res['std_pnl'] = daily_pnl.std()
	res['tot_pnl'] = daily_pnl.sum()
	res['num_days'] = len(daily_pnl)
	res['sharp_ratio'] = res['avg_pnl']/res['std_pnl']*np.sqrt(252.0)
	max_dd, max_dur = max_drawdown(cum_pnl)
	res['max_drawdown'] =  max_dd
	res['max_dd_period'] =  max_dur
	if abs(max_dd) > 0:
		res['profit_dd_ratio'] = res['all_profit']/abs(max_dd)
	else:
		res['profit_dd_ratio'] = 0
	return res, daily_pnl 

def get_trade_stats(trade_list):
	res = {}
	res['n_trades'] = len(trade_list)
	res['all_profit'] = sum([trade.profit for trade in trade_list])
	res['win_profit'] = sum([trade.profit for trade in trade_list if trade.profit>0])
	res['loss_profit'] = sum([trade.profit for trade in trade_list if trade.profit<0])
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
