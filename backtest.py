import datetime
import pandas as pd

class SimTrade(object):
	def __init__(self, inst='', entry=0, pos=0, pexit=0, start_time=None):
		self.inst = inst
		self.pos = pos
		self.direction = 1 if pos > 0 else -1
		self.price_in = entry
		self.exit = pexit
		self.start_time = start_time
		self.profit = 0
		self.end_time = None
		self.price_out = 0.0
		self.is_closed = False
	
	def open(self, price, pos, pexit, start_time):
		self.pos = pos
		self.direction = 1 if pos > 0 else -1
		self.price_in = price
		self.exit = pexit
		self.start_time = start_time
		self.is_closed = False
		
	def close(self, price, end_time):
		self.end_time = end_time
		self.price_out = price
		self.profit = (self.price_out - self.price_in) * self.pos
		self.is_closed = True

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
			cur_hwm = max(hwm[last_t], ts_idx[t])
			hwm[t] = cur_hwm
			drawdown[t]= hwm[t] - ts[t]
			duration[t]= 0 if drawdown[t] == 0 else duration[last_t] + 1
		last_t = t
	return drawdown.max(), duration.max()
