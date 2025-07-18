class TickData(object):
        """ Stores a single unit of data """

        def __init__(self, timestamp='', symbol='',
                                open_price=0, close_price=0, total_volume=0):
                self.symbol = symbol
                self.timestamp = timestamp
                self.open_price = open_price
                self.close_price = close_price
                self.total_volume = total_volume


class MarketData(object):
        def __init__(self):
                self.recent_ticks = dict()  # indexed by symbol

        def add_tick_data(self, tick_data):
                self.recent_ticks[tick_data.symbol] = tick_data

        def get_open_price(self, symbol):
                return self.get_tick_data(symbol).open_price

        def get_close_price(self, symbol):
                return self.get_tick_data(symbol).close_price

        def get_tick_data(self, symbol):
                return self.recent_ticks.get(symbol, TickData())

        def get_timestamp(self, symbol):
                return self.recent_ticks[symbol].timestamp


class MarketDataSource(object):
    def __init__(self, symbol, tick_event_handler=None, start='', end=''):
        self.market_data = MarketData()

        self.symbol = symbol
        self.tick_event_handler = tick_event_handler
        self.start, self.end = start, end
        self.df = None

    def fetch_historical_prices(self):
        import quandl

        # Update your Quandl API key here...
        QUANDL_API_KEY = 'BCzkk3NDWt7H9yjzx-DY'
        quandl.ApiConfig.api_key = QUANDL_API_KEY
        df = quandl.get(self.symbol, start_date=self.start, end_date=self.end)
        return df

    def run(self):
        if self.df is None:
            self.df = self.fetch_historical_prices()

        total_ticks = len(self.df)
        print('Processing total_ticks:', total_ticks)

        for timestamp, row in self.df.iterrows():
            open_price = row['Open']
            close_price = row['Close']
            volume = row['Volume']

            print(timestamp.date(), 'TICK', self.symbol,
                  'open:', open_price,
                  'close:', close_price)
            tick_data = TickData(timestamp, self.symbol, open_price,
                                close_price, volume)
            self.market_data.add_tick_data(tick_data)

            if self.tick_event_handler:
                self.tick_event_handler(self.market_data)


class Order(object):
        def __init__(self, timestamp, symbol,
                qty, is_buy, is_market_order,
                price=0
        ):
                self.timestamp = timestamp
                self.symbol = symbol
                self.qty = qty
                self.price = price
                self.is_buy = is_buy
                self.is_market_order = is_market_order
                self.is_filled = False
                self.filled_price = 0
                self.filled_time = None
                self.filled_qty = 0


class Position(object):
        def __init__(self, symbol=''):
                self.symbol = symbol
                self.buys = self.sells = self.net = 0
                self.rpnl = 0
                self.position_value = 0

        def on_position_event(self, is_buy, qty, price):
                if is_buy:
                        self.buys += qty
                else:
                        self.sells += qty

                self.net = self.buys - self.sells
                changed_value = qty * price * (-1 if is_buy else 1)
                self.position_value += changed_value

                if self.net == 0:
                        self.rpnl = self.position_value
                        self.position_value = 0

        def calculate_unrealized_pnl(self, price):
                if self.net == 0:
                        return 0

                market_value = self.net * price
                upnl = self.position_value + market_value
                return upnl


from abc import abstractmethod

class Strategy:
        def __init__(self, send_order_event_handler):
                self.send_order_event_handler = send_order_event_handler

        @abstractmethod
        def on_tick_event(self, market_data):
                raise NotImplementedError('Method is required!')

        @abstractmethod
        def on_position_event(self, positions):
                raise NotImplementedError('Method is required!')

        def send_market_order(self, symbol, qty, is_buy, timestamp):
                if self.send_order_event_handler:
                        order = Order(
                                timestamp,
                                symbol,
                                qty,
                                is_buy,
                                is_market_order=True,
                                price=0,
                        )
                        self.send_order_event_handler(order)


import pandas as pd

class MeanRevertingStrategy(Strategy):
    def __init__(self, symbol, trade_qty,
        send_order_event_handler=None, lookback_intervals=20,
        buy_threshold=-1.5, sell_threshold=1.5
    ):
        super(MeanRevertingStrategy, self).__init__(
            send_order_event_handler)

        self.symbol = symbol
        self.trade_qty = trade_qty
        self.lookback_intervals = lookback_intervals
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

        self.prices = pd.DataFrame()
        self.is_long = self.is_short = False

    def on_position_event(self, positions):
        position = positions.get(self.symbol)

        self.is_long = position and position.net > 0
        self.is_short = position and position.net < 0

    def on_tick_event(self, market_data):
        self.store_prices(market_data)

        if len(self.prices) < self.lookback_intervals:
            return

        self.generate_signals_and_send_order(market_data)

    def store_prices(self, market_data):
        timestamp = market_data.get_timestamp(self.symbol)
        close_price = market_data.get_close_price(self.symbol)
        self.prices.loc[timestamp, 'close'] = close_price

    def generate_signals_and_send_order(self, market_data):
        signal_value = self.calculate_z_score()
        timestamp = market_data.get_timestamp(self.symbol)

        if self.buy_threshold > signal_value and not self.is_long:
            print(timestamp.date(), 'BUY signal')
            self.send_market_order(
                self.symbol, self.trade_qty, True, timestamp)
        elif self.sell_threshold < signal_value and not self.is_short:
            print(timestamp.date(), 'SELL signal')
            self.send_market_order(
                self.symbol, self.trade_qty, False, timestamp)

    def calculate_z_score(self):
        self.prices = self.prices[-self.lookback_intervals:]
        returns = self.prices['close'].pct_change().dropna()
        z_score = ((returns - returns.mean()) / returns.std())[-1]
        return z_score



class BacktestEngine:
        def __init__(self, symbol, trade_qty, start='', end=''):
                self.symbol = symbol
                self.trade_qty = trade_qty
                self.market_data_source = MarketDataSource(
                        symbol,
                        tick_event_handler=self.on_tick_event,
                        start=start, end=end
                )

                self.strategy = None
                self.unfilled_orders = []
                self.positions = dict()
                self.df_rpnl = None

        def start(self, **kwargs):
                print('Backtest started...')

                self.unfilled_orders = []
                self.positions = dict()
                self.df_rpnl = pd.DataFrame()

                self.strategy = MeanRevertingStrategy(
                        self.symbol,
                        self.trade_qty,
                        send_order_event_handler=self.on_order_received,
                        **kwargs
                )
                self.market_data_source.run()

                print('Backtest completed.')

        def on_order_received(self, order):
                """ Adds an order to the order book """
                print(
                        order.timestamp.date(),
                        'ORDER',
                        'BUY' if order.is_buy else 'SELL',
                        order.symbol,
                        order.qty
                )
                self.unfilled_orders.append(order)

        def on_tick_event(self, market_data):
                self.match_order_book(market_data)
                self.strategy.on_tick_event(market_data)
                self.print_position_status(market_data)

        def match_order_book(self, market_data):
                if len(self.unfilled_orders) > 0:
                        self.unfilled_orders = [
                                order for order in self.unfilled_orders
                                if self.match_unfilled_orders(order, market_data)
                        ]

        def match_unfilled_orders(self, order, market_data):
                symbol = order.symbol
                timestamp = market_data.get_timestamp(symbol)

                """ Order is matched and filled """
                if order.is_market_order and timestamp > order.timestamp:
                        open_price = market_data.get_open_price(symbol)

                        order.is_filled = True
                        order.filled_timestamp = timestamp
                        order.filled_price = open_price

                        self.on_order_filled(
                                symbol, order.qty, order.is_buy,
                                open_price, timestamp
                        )
                        return False

                return True

        def on_order_filled(self, symbol, qty, is_buy, filled_price, timestamp):
                position = self.get_position(symbol)
                position.on_position_event(is_buy, qty, filled_price)
                self.df_rpnl.loc[timestamp, "rpnl"] = position.rpnl

                self.strategy.on_position_event(self.positions)

                print(
                        timestamp.date(),
                        'FILLED', "BUY" if is_buy else "SELL",
                        qty, symbol, 'at', filled_price
                )

        def get_position(self, symbol):
                if symbol not in self.positions:
                        self.positions[symbol] = Position(symbol)

                return self.positions[symbol]

        def print_position_status(self, market_data):
                for symbol, position in self.positions.items():
                        close_price = market_data.get_close_price(symbol)
                        timestamp = market_data.get_timestamp(symbol)

                        upnl = position.calculate_unrealized_pnl(close_price)

                        print(
                                timestamp.date(),
                                'POSITION',
                                'value:%.3f' % position.position_value,
                                'upnl:%.3f' % upnl,
                                'rpnl:%.3f' % position.rpnl
                        )

engine = BacktestEngine(
    'WIKI/AAPL', 1,
    start='2015-01-01',
    end='2017-12-31'
)

engine.start(
    lookback_intervals=20,
    buy_threshold=-1.5,
    sell_threshold=1.5
)


