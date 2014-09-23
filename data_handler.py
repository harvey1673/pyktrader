import datetime
import pandas as pd
from mysqlaccess import *

def conv_ohlc_freq(df, freq):
	highcol = pd.DataFrame(df.high).resample(freq, how ='max').dropna()
	lowcol  = pd.DataFrame(df.low).resample(freq, how ='min').dropna()
	opencol = pd.DataFrame(df.open).resample(freq, how ='first').dropna()
	closecol= pd.DataFrame(df.close).resample(freq, how ='last').dropna()
	res =  pd.concat([opencol, highcol, lowcol, closecol], join='outer', axis =1)
	return res

def TR(df):
	tr_df = pd.concat([df.high-df.close, abs(df.high-df.close.shift(1)), abs(df.low--df.close.shift(1))], join='outer', axis=1)
	return tr_df.idxmax(1)

def ATR(df, window=20):
	tr = TR(df)
	atr = pd.stats.moments.ewma(tr, span=20)
