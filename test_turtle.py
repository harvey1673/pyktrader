import misc
import data_handler as dh
import pandas as pd
import backtest as sim
	
def turtle_sim( assets, start_date, end_date ):
	NN = 2
	start_idx = 20
	data = {}
	results = {}
	for pc in assets:
		data[pc] = misc.rolling_hist_data(pc, 1, start_date, end_date, '-20b', 'd', '-55b')
		res = {}
		for i in range(len(data[pc]):
			df = data[pc][i]['data']
            cont = data[pc][i]['contract']
			res[cont] = {}
            expiry = df.index[-1].date()
			ts = dh.ATR(df, n=20)
			df.join(ts)
			ts = dh.DONCH(df, 55):
			df.join(ts)
			ts = dh.DONCH(df, 20)
			df.join(ts)
			ts = dh.DONCH(df, 10)
			df.join(ts)
            ll = df.shape[0]
            df['pos'] = pd.Series([0]*ll, index = df.index)
            df['OL_1'] = pd.concat([df.DONCH_H20.shift(1), df.open], join='outer', axis=1).max(axis=1)
            df['OS_1'] = pd.concat([df.DONCH_L20.shift(1), df.open], join='outer', axis=1).min(axis=1)
            df['CL_1'] = pd.concat([df.DONCH_L10.shift(1), df.open], join='outer', axis=1).min(axis=1)
            df['CS_1'] = pd.concat([df.DONCH_H10.shift(1), df.open], join='outer', axis=1).max(axis=1)
            #df['OL_2'] = pd.concat([df.DONCH_H55.shift(1), df.open], join='outer', axis=1).max(axis=1)
            #df['OS_2'] = pd.concat([df.DONCH_L55.shift(1), df.open], join='outer', axis=1).min(axis=1)
            #df['CL_2'] = pd.concat([df.DONCH_L20.shift(1), df.open], join='outer', axis=1).min(axis=1)
            #df['CS_2'] = pd.concat([df.DONCH_H20.shift(1), df.open], join='outer', axis=1).max(axis=1)
			curr_pos = []
			closed_trades = []
			for idx, dd in enumerate(df.index):
				tdate = dd.date()
                u = df[dd]
				n_unit = 0
                if idx < start_idx:
                    u.pos = 0
                    last_pos = u.pos
					last_price = u.close
                    continue
                if len(curr_pos) == 0 and idx < len(df.index)-1:
					entry = 0
                    if u.close > u.OL_1:
                        #n_unit = min(max(int((u.close - u.OL_1)*2.0/u.ATR_20 + 1),0),4)
						n_unit = 1
						direction = 1
                        entry = u.OL_1
					elif u.close > u.OS_1:
						#n_unit = min(max(int((u.OS_1 - u.low) *2.0/u.ATR_20 + 1),0),4)
						n_unit = 1
						direction = -1
                        entry = u.OS_1
					u.new_pos = n_unit * direction
					last_pos = n_unit * direction
					if entry > 0:
						trade = sim.SimTrade(cont, entry, direction, entry- direction * u.ATR_20 * NN, dd)
						curr_pos.append(trade)
				else:
                    direction = curr_pos[0].direction
                    tot_pos = sum([trade.pos * trade.direction for trade in curr_pos])
					#exit position out of channel
                    if (direction == 1 and u.close < u.CL_1) or (direction == -1 and u.close > u.CS_1) or (idx == len(df.index)-1):
						for trade in curr_pos:
							trade.close( u.close, dd )
							closed_trades.append(trade)
                        u.pnl = sum([trade.profit for trade in curr_pos])
                        curr_pos = []
					#stop loss position partially
                    elif (curr_pos[-1].exit - u.close) * direction >= 0:
						for trade in curr_pos:
							if (trade.exit - u.close) * direction > 0:
								trade.close(u.close, dd)
								closed_trades.append(trade)
                        u.pnl = sum([trade.profit for trade in curr_pos if trade.is_closed])    
						curr_pos = [pos for trade in curr_pos if not trade.is_closed]
					#add positions
					elif (tot_pos < 4) and (u.close - curr_pos[-1].price_in)*direction > u.ATR_20/2.0:
						diff = u.close - curr_pos[-1].price_in
						for trade in curr_pos:
							trade.exit += diff
						trade = sim.SimTrade(cont, u.close, direction, u.close - direction * u.ATR_20 * NN, dd)
						curr_pos.append(trade)
				u.pos = sum( [trade.pos for trade in curr_pos] )	
			df['pnl'] = df['pos'].shift(1)*(df['close'] - df['close'].shift(1))
			df['cum_pnl'] = df['pnl'].cumsum()
			drawdown_i = np.argmax(np.maximum.accumulate(df['cum_pnl']) - df['cum_pnl'])
			drawdown_j = np.argmax(df['cum_pnl'][:drawdown_i])
			daily_pnl = pd.Series(df['pnl']).resample('1d',how='sum')
			daily_pnl.name = 'dailyPNL'
			res[cont]['avg_pnl'] = daily_pnl.mean()
			res[cont]['std_pnl'] = daily_pnl.std()
			res[cont]['tot_pnl'] = daily_pnl.sum()
			res[cont]['num_days'] = len(daily_pnl)
			res[cont]['drawdown_i'] =  drawdown_i
			res[cont]['drawdown_j'] =  drawdown_j
			res[cont]['n_trades'] = len(closed_trades)
			res[cont]['all_profit'] = sum([trade.profit for trade in closed_trades])
			res[cont]['win_profit'] = sum([trade.profit for trade in closed_trades if trade.profit>0])
			res[cont]['loss_profit'] = sum([trade.profit for trade in closed_trades if trade.profit<0])
			res[cont]['num_win'] = len([trade.profit for trade in closed_trades if trade.profit>0])
			res[cont]['num_loss'] = len([trade.profit for trade in closed_trades if trade.profit<0])
			res[cont]['win_ratio'] = results[pc][cont]['num_win']/results[pc][cont]['n_trades']
			res[cont]['profit_per_win'] = results[pc][cont]['win_profit']/results[pc][cont]['num_win']
			res[cont]['profit_per_loss'] = results[pc][cont]['loss_profit']/results[pc][cont]['num_loss']
			results[pc] = pd.DataFrame.from_dict(res)
	return results

