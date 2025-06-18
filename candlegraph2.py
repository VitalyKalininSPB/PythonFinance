import yfinance as yf
import mplfinance as mpf
import pandas as pd
import numpy as np

aapl = yf.Ticker('AAPL')

start_date = "2023-01-01"
end_date = "2024-11-20"
stock_data = aapl.history(start=start_date, end=end_date)

stock_data['20MA'] = stock_data['Close'].rolling(20).mean()
stock_data['60MA'] = stock_data['Close'].rolling(60).mean()

stock_data['buy_signal'] = np.where((stock_data['20MA'] > stock_data['60MA']) & (stock_data['20MA'].shift(1) <= stock_data['60MA'].shift(1)),
	stock_data['High'] + 2,
	np.nan)

stock_data['sell_signal'] = np.where((stock_data['20MA'] <= stock_data['60MA']) & (stock_data['20MA'].shift(1) > stock_data['60MA'].shift(1)),
	stock_data['High'] + 2,
	np.nan)

stock_data['Position'] = stock_data['20MA'] > stock_data['60MA']
stock_data['Performance'] = np.where(stock_data['Position'].shift(1) & stock_data['Position'],
					stock_data['Close'] / stock_data['Close'].shift(1),
					1).cumprod() - 1

ad_plot = [mpf.make_addplot(stock_data['20MA'], color='blue', label='MA 20'),
	   mpf.make_addplot(stock_data['60MA'], color='blue', label='MA 60'),
	   mpf.make_addplot(stock_data['buy_signal'], type='scatter', markersize=40, marker='^', color='green', label='buy signal'),
   	   mpf.make_addplot(stock_data['sell_signal'], type='scatter', markersize=40, marker='v', color='red', label='sell signal'),
   	   mpf.make_addplot(stock_data['Performance'], type='line', color='blue', panel=2)]


mpf.plot(stock_data, type='candle',
	hlines=dict(hlines=[196,180],
		colors=['green', 'red'],
		linestyle='-.'),
	vlines=dict(vlines=['2024-01-24', '2024-03-01'],
		colors='yellow'),
	addplot=ad_plot,
	volume=True)
