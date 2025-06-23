import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import seaborn as sb

stonks = ["META", "GS", "NVDA", "MSFT", "TSLA", "AAPL", "CCL", "BA"]

start = dt.datetime(2025,1,1)
end = dt.datetime.now()

# get data
coll = yf.download(stonks, start=start, end=end, interval='1d', group_by='tickers')

# Clean up columns
to_drop = ['Open', 'High', 'Low', 'Volume']
price_close = coll.drop(to_drop, level=1, axis=1)

# Describe it
print(price_close.describe())

corr_data = price_close.pct_change().corr(method="pearson")
print(corr_data)
sb.heatmap(corr_data, annot=True, cmap="coolwarm")

plt.show()
