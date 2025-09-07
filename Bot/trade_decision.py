class TradeDecision:

    def __init__(self, row):
        self.signal = row.trade_signal
        self.symbol = row.symbol
        self.last_close_price = row.close
        

    def __repr__(self):
        return f"TradeDecision():  dir:{self.signal}  symbol:{self.symbol}"
