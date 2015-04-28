import matplotlib
matplotlib.use('TkAgg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick
from matplotlib.finance import candlestick2
import chart
import mysqlaccess as db
import datetime

d_start = datetime.date(2015,1,2)
d_end = datetime.date(2015,4,24)
dbtable = 'fut_daily'
inst = 'm1509'
df = db.load_daily_data_to_df(dbtable, inst, d_start, d_end)
ohlc = pd.DataFrame(df)
ohlc = ohlc.drop(u'openInterest', 1)
ohlc = ohlc.drop('volume', 1)
fig = plt.figure()
ax = fig.add_subplot(311)
y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
ax.yaxis.set_major_formatter(y_formatter)
chart.cchart(ax, ohlc, width=.5, colorup='g', colordown='r', alpha=1)
#ohlc.plot(ax=ax)
ax.set_xticks(np.arange(0,len(ohlc.index),5))
#plt.savefig("1.png")
plt.show()
