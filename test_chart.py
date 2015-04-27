import matplotlib
matplotlib.use('TkAgg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick
from matplotlib.finance import candlestick2
import chart

eur = pd.read_csv("C:/Users/CZ61217/eu.csv")
e = eur.set_index(pd.to_datetime(eur['Time']))
e = e.drop('Time',1)
e = e.drop('Ask',1)
e = e.drop('AskVolume',1)
e = e.drop('BidVolume',1)

e.to_csv("eu2.csv",float_format='%.5f', date_format='%Y-%m-%d %H:%M:%S')
e = pd.read_csv("eu2.csv")
e = e.set_index('Time')

x = range(len(e.Bid))
y = [i/200 for i in x]
e['n'] = y

o=e.groupby('n').head(1)
tindex = o.index.levels[1]
o=o.set_index('n')
o.rename(columns={'Bid':'Open'}, inplace=True)

h=e.groupby('n').aggregate(np.max)
h.rename(columns={'Bid':'High'}, inplace=True)
l=e.groupby('n').aggregate(np.min)
l.rename(columns={'Bid':'Low'}, inplace=True)
c=e.groupby('n').tail(1)
c=c.set_index('n')
c.rename(columns={'Bid':'Close'}, inplace=True)

ohlc = o.join(h).join(l).join(c)
ohlc = ohlc.set_index(tindex)
ohlc.index.name = 'Time'
#ohlc = ohlc[:50]

fig = plt.figure()
ax = fig.add_subplot(111)
y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
ax.yaxis.set_major_formatter(y_formatter)
chart.cchart(ax, ohlc['Open'], ohlc['Close'], ohlc['High'], ohlc['Low'], width=.5, colorup='g', colordown='r', alpha=1)
#ax.set_xticks(tindex)
plt.savefig("1.png")
plt.show()
