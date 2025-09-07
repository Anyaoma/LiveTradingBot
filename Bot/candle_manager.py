from api_call.alpaca import AlpacaApi
from Bot.candle_timing import CandleTiming


class CandleManager: #Do we have a new candle

    def __init__(self, api:AlpacaApi, tickers, log_message, granularity):
        self.api = AlpacaApi
        self.tickers = tickers
        self.log_message = log_message
        self.granularity = granularity
        self.asset_list = tickers
        self.timings = {pair: CandleTiming(self.api.last_complete_candle(pair, self.granularity)) for pair in self.asset_list} #for all the pairs, get their last candle time and store them in a adictionary
        for pair, timing in self.timings.items():
            self.log_message(f" CandleManager() init last_candle: {timing}", pair) #log message intofile



    def update_timings(self):
        assets_with_new_candles = []

        for asset in self.asset_list:
            current = self.api.last_complete_candle(asset, self.granularity)
            if current is None:
                self.log_message(f"Unable to get candle", asset)
                continue
            self.timings[asset].is_ready = False
            if current > self.timings[asset].last_time:
                self.timings[asset].is_ready = True
                self.timings[asset].last_time = current
                self.log_message(f"CandleManager() new candle: {self.timings[asset]}",asset)
                assets_with_new_candles.append(asset)

        return assets_with_new_candles