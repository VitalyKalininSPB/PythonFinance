import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader as web
import yfinance as yf
import talib as ta

start = dt.datetime(2024,1,1)
end = dt.datetime.now()

ticker = 'NVDA'
data = yf.download(tickers=ticker, start=start, end=end, multi_level_index=False)

data['SMA_100']  = ta.SMA(data['Close'], timeperiod=100)

# EMA for example

plt.plot(data['Close'])
plt.plot(data['SMA_100'])
plt.show()

data['RSI'] = ta.RSI(data['Close'])

fig, axs = plt.subplots(2, 1)

axs[0].plot(data['Close'])
axs[1].axhline(y=70, color="r", linestyle="--")
axs[1].axhline(y=30, color="g", linestyle="--")
axs[1].plot(data['RSI'], color="orange")

data['LINEARREG'] = ta.LINEARREG(data['Close'], 200)
plt.plot(data['Close'])
plt.plot(data['LINEARREG'])
plt.show()
