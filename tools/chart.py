import datetime
import numpy as np
from matplotlib import verbose, get_cachedir
from matplotlib.dates import date2num
from matplotlib.cbook import iterable, mkdirs
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import colorConverter
from matplotlib.lines import Line2D, TICKLEFT, TICKRIGHT
from matplotlib.patches import Rectangle
from matplotlib.transforms import Affine2D

def cchart(ax, ohlc_df, width=4,
                 colorup='k', colordown='r',
                 alpha=0.75,
                ):
    """
    Represent the open, close as a bar line and high low range as a
    vertical line.
    ax          : an Axes instance to plot to
    width       : the bar width in points
    colorup     : the color of the lines where close >= open
    colordown   : the color of the lines where close <  open
    alpha       : bar transparency

    return value is lineCollection, barCollection
    """

    # note this code assumes if any value open, close, low, high is
    # missing they all are missing

    delta = width/2.
    barVerts = [ ( (i-delta, open), (i-delta, close), (i+delta, close), (i+delta, open) ) for i, open, close in zip(xrange(len(ohlc_df.open)), ohlc_df.open, ohlc_df.close) if open != -1 and close!=-1 ]

    #rangeSegments = [ ((i, low), (i, high)) for i, low, high in zip(xrange(len(ohlc_df.low)), ohlc_df.low, ohlc_df.high) if low != -1 ]
    rangeSegments = [ ((i, max(open, close)), (i, high)) for i, high, open, close in zip(xrange(len(ohlc_df.high)), ohlc_df.high, ohlc_df.open, ohlc_df.close) if high!=-1 ]
    rangeSegments2 = [ ((i, low), (i, min(open, close))) for i, low, open, close in zip(xrange(len(ohlc_df.low)), ohlc_df.low, ohlc_df.open, ohlc_df.close) if low!=-1]

    r,g,b = colorConverter.to_rgb(colorup)
    colorup = r,g,b,alpha
    r,g,b = colorConverter.to_rgb(colordown)
    colordown = r,g,b,alpha
    colord = { True : colorup,
               False : colordown,
               }
    colors = [colord[open<close] for open, close in zip(ohlc_df.open, ohlc_df.close) if open!=-1 and close !=-1]


    assert(len(barVerts)==len(rangeSegments))

    useAA = 0,  # use tuple here
    lw = 0.5,   # and here
    rangeCollection = LineCollection(rangeSegments,
                                     colors       = ( (0,0,0,1), ),
                                     linewidths   = lw,
                                     antialiaseds = useAA,
                                     )

    rangeCollection2 = LineCollection(rangeSegments2,
                                     colors       = ( (0,0,0,1), ),
                                     linewidths   = lw,
                                     antialiaseds = useAA,
                                     )

    barCollection = PolyCollection(barVerts,
                                   facecolors   = colors,
                                   edgecolors   = ( (0,0,0,1), ),
                                   antialiaseds = useAA,
                                   linewidths   = lw,
                                   )

    minx, maxx = 0, len(rangeSegments)
    miny = min([low for low in ohlc_df.low if low !=-1])
    maxy = max([high for high in ohlc_df.high if high != -1])

    corners = (minx, miny), (maxx, maxy)
    ax.update_datalim(corners)
    ax.autoscale_view()

    # add these last
    ax.add_collection(rangeCollection)
    ax.add_collection(rangeCollection2)
    ax.add_collection(barCollection)
    return rangeCollection, barCollection
	
