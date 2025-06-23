import yfinance as yf
import talib as ta
import plotly.graph_objs as go
import plotly.io as pio
from plotly.subplots import make_subplots

pio.renderers.default = 'browser'

ticker = 'AAPL'
start_date = '2023-01-01'
end_date = '2024-01-01'

df = yf.download(ticker, start_date, end_date, multi_level_index=False)
df['SMA'] = ta.SMA(df['Close'], timeperiod=20)
df['RSI'] = ta.RSI(df['Close'], timeperiod=20)
df['Upper_BB'], df['Middle_BB'], df['Lower_BB'] = ta.BBANDS(df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.2, row_heights=[0.7, 0.3],
        subplot_titles=[f'{ticker} Price and Indicators', 'RSI'])


candlestick = go.Candlestick(
    x=df.index,
    open=df.Open,
    high=df.High,
    low=df.Low,
    close=df.Close,
    name='Price'
)

sma_line = go.Scatter(
    x=df.index,
    y=df.SMA,
    line={'color': 'blue', 'width': 2},
    name='SMA'
    )


upper_bb = go.Scatter(
    x=df.index,
    y=df['Upper_BB'],
    line={'color': 'red', 'width': 1},
    name='Upper BB'
    )

lower_bb = go.Scatter(
    x=df.index,
    y=df['Lower_BB'],
    line={'color': 'red', 'width': 1},
    name='Lower BB'
    )

middle_bb = go.Scatter(
    x=df.index,
    y=df['Middle_BB'],
    line={'color': 'red', 'width': 1},
    name='Middle BB'
    )


fig.add_trace(candlestick, row=1, col=1)
fig.add_trace(sma_line, row=1, col=1)
fig.add_trace(upper_bb, row=1, col=1)
fig.add_trace(lower_bb, row=1, col=1)
fig.add_trace(middle_bb, row=1, col=1)

fig.update_layout(
    title=f'{ticker} Technical Analysis',
    yaxis_title='Price',
    xaxis_title='Date',
    xaxis_rangeslider_visible=False,
    height=800,
    template='plotly_dark'
    )


fig.show()
