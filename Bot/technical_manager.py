#DO WE HAVE A SIGNAL
#AFTER A NEW CANDLE IS CONFIRMED, WE LOAD DATA, PROCESS IT AND CHECK:
#DO WE HAVE A SIGNAL

import pandas as pd

pd.set_option('display.max_columns', None) #
pd.set_option('expand_frame_repr', False) #prevent it from making new lines and wrapping rows
from api_call.alpaca import AlpacaApi
import constants.constants as defs
from technical_indicators.indicators import *
from Bot.trade_decision import TradeDecision


ADDROWS = 20

def apply_stochastic(row):
    if row.change_K < 20:
        return 'oversold'
    elif row.change_K > 80:
        return 'overbought'
    return None

def apply_signal(row):
    if row.macd  > row.signal and row.prev_macd < row.prev_signal and row.stoch_signal=='oversold':
        return 'BUY'
    elif row.macd  < row.signal and row.prev_macd > row.prev_signal and row.stoch_signal=='overbought':
        return 'SELL'
    return None

def process_candles(df:pd.DataFrame, symbol, log_message):
    MACD(df)
    stochastic(df)
    df['prev_macd'] = df['macd'].shift(1)
    df['symbol'] = symbol
    df['prev_signal'] = df['signal'].shift(1)
    df['stoch_signal'] = df.apply(apply_stochastic, axis=1)
    df['trade_signal'] = df.apply(apply_signal, axis=1)

    return df.iloc[-1]

def fetch_candles(symbol, time_frame, row_count, candle_time, api: AlpacaApi, log_message):
    df = api.fetch_df(symbols=symbol,time_frame=time_frame, limit=row_count )
    if df is None or df.shape[0]==0:
        log_message("tech_manager fetch_candles failed to get candles", symbol)
        return None
    if df[symbol]['time'].iloc[-1] != candle_time:
        log_message(f"tech_manager fetch_candles {df.iloc[-1].time} not correct", symbol)
        return None
    
    return df[symbol]

def get_trade_decisions(candle_time, symbol, granularity, api: AlpacaApi, log_message):
    max_rows = ADDROWS
    log_message(f"tech_manager: max_rows:{max_rows}, candle_time:{candle_time}, granularity:{granularity}", symbol)

    df = fetch_candles(symbol,granularity ,max_rows, candle_time, api, log_message)

    if df is not None:
        last_row = process_candles(df, symbol, log_message)
        return TradeDecision(last_row)

    return None
#the get_trade_decision function will either return a none or an instance of tradeDecision class 