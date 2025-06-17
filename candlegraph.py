#raw = pd.read_csv('fxcm_eur_usd_eod_data.csv', index_col=0, parse_dates=True)

#quotes = raw[['AskOpen', 'AskHigh', 'AskLow', 'AskClose']]

import plotly.graph_objects as go

import pandas as pd
from datetime import datetime
import ta

df = pd.read_csv('fxcm_eur_usd_eod_data.csv')

df["rsi"] = ta.momentum.rsi(df["AskClose"], window=14, fillna=False)

#layoutt = go.Layout(autosize=False, width=4181, height=1597)
#layoutt = go.Layout(autosize=True)
#layoutt2 = go.Layout(autosize=False, width=6731, height=2571)

'''fig_001 = go.Figure(
    data=[
        go.Candlestick(
            x=df["Time"],
            open=df["AskOpen"],
            high=df["AskHigh"],
            low=df["AskLow"],
            close=df["AskClose"],
            name="OHLC",
        ),
        go.Scatter(
            x=df["Time"], y=df["rsi"], mode="markers+lines", name="RSI", yaxis="y2"
        ),
    ],
    layout=layoutt,
).update_layout(
    yaxis_domain=[0.3, 1],
    yaxis2={"domain": [0, 0.20]},
    xaxis_rangeslider_visible=False,
    showlegend=False,
)'''

#fig_001.show()


fig = go.Figure([
    go.Candlestick(
        x=df["Time"],
        open=df["AskOpen"],
        high=df["AskHigh"],
        low=df["AskLow"],
        close=df["AskClose"],
        name="OHLC",
    ),
    go.Scatter(
        x=df["Time"], y=df["rsi"], mode="markers+lines", name="RSI", yaxis="y2"
    )
])

fig.show()
