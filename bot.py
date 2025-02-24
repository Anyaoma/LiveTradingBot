import json
import time
from instruments.log_wrapper import LogWrapper
from models.trade_settings import TradeSettings
from oanda_api.Oanda_api import OandaApi
from bot.candle_manager import CandleManager
from bot.technicals_manager import get_trade_decision
import constants.defs as defs
from bot.trade_manager import place_trade



class Bot:

    ERROR_LOG = 'error'
    MAIN_LOG = 'main'
    GRANULARITY = 'M5'
    SLEEP = 10 #time to sleep between checking for a new candle.

    def __init__(self):
        self.load_settings()
        self.setup_logs()

        self.api = OandaApi()
        self.candle_manager = CandleManager(self.api, self.trade_settings, self.log_message, Bot.GRANULARITY) #this instantiates ou candle manager class and logs in each pair files the timing of the last completed candle
        self.log_to_main('Bot started')
        self.log_to_error('Bot started')

    def load_settings(self):
        with open("./bot/settings.json", 'r') as f:
            data = json.loads(f.read())
            self.trade_settings = {k: TradeSettings(v, k) for k, v in data['pairs'].items()}
            self.trade_risk = data['trade_risk']

    def setup_logs(self):
        #we can assess the logs by using the keys specifically. once weve assessed it, we can use the .logger.info/ .error or whatever we want to log something.
        self.logs = {}
        #set up logs for each of the pairs we are trying to trade
        for k in self.trade_settings.keys():
            self.logs[k] = LogWrapper(k)
            self.log_message(f"{self.trade_settings[k]}", k)
        self.logs[Bot.ERROR_LOG] = LogWrapper(Bot.ERROR_LOG) 
        self.logs[Bot.MAIN_LOG] = LogWrapper(Bot.MAIN_LOG)
        self.log_to_main(f"Bot started with {TradeSettings.settings_to_str(self.trade_settings)}")

    def log_message(self, msg, key):
        self.logs[key].logger.debug(msg)#

    def log_to_main(self, msg):
        self.log_message(msg, Bot.MAIN_LOG)

    def log_to_error(self, msg):
        self.log_message(msg, Bot.ERROR_LOG)

    def process_candles(self, triggered):#do something with the list returned from the candle_manager update timings
        if len(triggered) > 0:
            self.log_message(f"process_candles triggered: {triggered}",Bot.MAIN_LOG)
            for p in triggered:#add the logic to decide whether we want to make a trade or not by calculating our indicators.
                last_time = self.candle_manager.timings[p].last_time
                trade_decision = get_trade_decision(last_time, p, Bot.GRANULARITY, self.api, self.trade_settings[p], self.log_message) 

                if trade_decision is not None and trade_decision.signal != defs.NONE:
                    self.log_message(f"place trade {trade_decision}", p)
                    self.log_to_main(f"place trade {trade_decision}")
                    place_trade(trade_decision, self.api, self.log_message, self.log_to_error, self.trade_risk)

    def run(self): #run our bot to check for new candles. our entry point into the prograam
        while True:
            time.sleep(Bot.SLEEP) #sleep for the seconds we defined
            #use the candle manager to update timing
            try: 
                self.process_candles(self.candle_manager.update_timings())#returns a list of all the pairs that has been updated
            except Exception as error:
                self.log_to_error(f"CRASH: {error}")
                break
            


