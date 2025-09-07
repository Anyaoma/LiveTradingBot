import json
import time
from Log_file import LogWrapper
#from models.trade_settings import TradeSettings
from api_call.alpaca import AlpacaApi
from Bot.candle_manager import CandleManager
from Bot.technical_manager import get_trade_decision
from alpaca.trading.client import TradingClient
import constants.constants as defs
from Bot.trade_manager import place_trade


class Bot:
    ERROR_LOG = 'error'
    MAIN_LOG = 'main'
    GRANULARITY = 'M1'
    SLEEP = 10
    TICKERS = ['AAPL','GOOGL','CSCO']

    def __init__(self):
        self.setup_logs()
        self.api_client = TradingClient(defs.api_key, defs.api_secret, paper=True)
        self.api = AlpacaApi()
        self.candle_manager = CandleManager(self.api, Bot.TICKERS, self.log_message, Bot.GRANULARITY) #this instantiates the candles manager class with its attributes


    def setup_logs(self):
        self.logs = {}
        for k in Bot.TICKERS:
            self.logs[k] = LogWrapper(k)
            self.log_message(f'Instrument: {k}', k) #write a message in the log file introducing the instruments
        self.logs[Bot.ERROR_LOG] = LogWrapper(Bot.ERROR_LOG)
        self.logs[Bot.MAIN_LOG] = LogWrapper(Bot.MAIN_LOG)

    
    def log_message(self, msg, key):
        self.logs[key].logger.debug(msg)

    def log_to_main(self,msg):
        self.log_message(msg, Bot.MAIN_LOG)

    def log_to_error(self, msg):
        self.log_message(msg, Bot.ERROR_LOG)

    def process_candles(self, assets_with_new_candles):
        if len(assets_with_new_candles)> 0:
            self.log_message(f"process_candles triggered: {assets_with_new_candles}",Bot.MAIN_LOG)
            for p in assets_with_new_candles:#add the logic to decide whether we want to make a trade or not by calculating our indicators.
                last_time = self.candle_manager.timings[p].last_time
                trade_decision = get_trade_decision(last_time, p, Bot.GRANULARITY, self.api, self.log_message) 

                if trade_decision is not None and trade_decision.signal != None:
                    self.log_message(f"place trade {trade_decision}", p)
                    self.log_to_main(f"place trade {trade_decision}")
                    place_trade(trade_decision, self.api,self.api_client, self.log_message, self.log_to_error, self.trade_risk)


    def run_once(self):
        try:
            self.process_candles(self.candle_manager.update_timings())
        except Exception as error:
            self.log_to_error(f'CRASH: {error}')


    def shutdown(self):
        try:
            self.log_to_main("Shutting down... Closing all positions.")
            self.api_client.close_all_positions()
            time.sleep(10)
            self.api_client.cancel_orders()
            time.sleep(10)
        except Exception as e:
            self.log_to_error(f"Error during shutdown: {e}")
    

#Lastly, using the time module, you can run the main function iteratively based on whatever candle youre working with e.g 900 for a 15min candle
if __name__ == "__main__":
    bot = Bot()
    start_time = time.time()
    timeout = start_time + 60 * 60 * 1  # 1 hour

    try:
        while time.time() <= timeout:
            print(f'Starting iteration at {time.strftime("%Y-%m-%d %H:%M:%S")}')
            bot.run_once()
            time.sleep(900 - ((time.time() - start_time) % 900))  # wait for next 15m bar
    finally:
        bot.shutdown()
