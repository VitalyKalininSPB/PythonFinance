import pandas as pd

df = pd.read_csv('SPY_20110701_20120630_Bollinger.csv',index_col=0,parse_dates=True)
df.shape
df.head(3)
df.tail(3)

import mplfinance as mpf

tcdf = df[['LowerB','UpperB']]  # DataFrame with two columns

def percentB_aboveone(percentB,price):
    import numpy as np
    signal   = []
    previous = 2
    for date,value in percentB.items():
        if value > 1 and previous <= 1:
            signal.append(price[date]*1.01)
        else:
            signal.append(np.nan)
        previous = value
    return signal

def percentB_belowzero(percentB,price):
    import numpy as np
    signal   = []
    previous = -1.0
    for date,value in percentB.items():
        if value < 0 and previous >= 0:
            signal.append(price[date]*0.99)
        else:
            signal.append(np.nan)
        previous = value
    return signal

low_signal  = percentB_belowzero(df['PercentB'], df['Close'])
high_signal = percentB_aboveone(df['PercentB'], df['Close'])

apds = [ mpf.make_addplot(tcdf),
         mpf.make_addplot(low_signal,type='scatter',markersize=200,marker='^'),
         mpf.make_addplot(high_signal,type='scatter',markersize=200,marker='v'),
       ]

mpf.plot(df,addplot=apds,figscale=1.25,volume=True)
