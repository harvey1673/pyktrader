import misc
import data_handler as dh
import pandas as pd


#Donchian Channel
def DONCH(df, n):
    DC_H = pd.rolling_max(df['high'],n)
    DC_H.name = 'DonchianH_'+ str(n)
    DC_L = pd.rolling_min(df['low'], n)
    DC_L.name = 'DonchianL_'+ str(n)
    return pd.concat([DC_H, DC_L], join='outer', axis=1)
	
def turtle_sim( assets, start_date, end_date ):
	data = {}
	for pc in assets:
		data[pc] = misc.rolling_hist_data(pc, 1, start_date, end_date, '-20b', 'd', '-55b')
		for i in range(len(data[pc]):
			df = data[pc][i]['data']
			ts = dh.ATR(df, n=20)
			df.join(ts)
			ts = dh.DONCH_H(df, 55):
			df.join(ts)
			ts = dh.DONCH_L(df, 55):
			df.join(ts)
			ts = dh.DONCH_H(df, 20)
			df.join(ts)
			ts = dh.DONCH_L(df, 20):
			df.join(ts)
			ts = dh.DONCH_H(df, 10)
			df.join(ts)
			ts = dh.DONCH_L(df, 10)
			df.join(ts)
			cont = data[pc][i]['contract']
			expiry = df.index[-1].date()
			for idx, dd in enumerate(df.index):
				d = dd.date()
		
