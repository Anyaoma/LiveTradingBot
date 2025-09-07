from api_call.alpaca import AlpacaApi
from Bot.trade_decision import TradeDecision
from alpaca.trading.requests import MarketOrderRequest, TrailingStopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.client import TradingClient
import constants.constants as defs
import time


max_pos = 3000


def quantity(last_traded_price):#determine quantity to trade based on last traded price of ticker and amount available to trade
    return int(max_pos/last_traded_price)

def trade_is_open(symbol, api:AlpacaApi, api_client: TradingClient):
    open_trades = api_client.get_all_positions()
    for ot in open_trades:
        if ot.symbol == symbol:
            return ot
    return None

def take_trade(trade_decision:TradeDecision, api:AlpacaApi, api_client:TradingClient, log_message, log_error):
    if trade_decision.signal == 'BUY':
        order = MarketOrderRequest(symbol=trade_decision.symbol, qty=max(1,quantity(trade_decision.close), side=OrderSide.BUY, time_in_force=TimeInForce.IOC ))
        api_client.submit_order(order)
        time.sleep(2) #add a lag to allow python execute your trade
        log_message(f'Bought {max(1,quantity(trade_decision.symbol))} stocks in {trade_decision.symbol}')
        try:
            filled_qty = api_client.get_open_position(trade_decision.symbol).qty 
            time.sleep(1)
            trailing_order = TrailingStopOrderRequest(symbol=trade_decision.symbol, qty=int(filled_qty), side=OrderSide.SELL, time_in_force=TimeInForce.DAY, trail_percent=1.5)
            api_client.submit_order(trailing_order)
            return {
            "entry_order": order,
            "trailing_order": trailing_order,
            "symbol": trade_decision.symbol}
        except Exception as e:
            log_error(e)
            return None

    if trade_decision.signal == 'SELL':
        order = MarketOrderRequest(symbol=trade_decision.symbol, qty=max(1,quantity(trade_decision.close), side=OrderSide.SELL, time_in_force=TimeInForce.IOC ))
        api_client.submit_order(order)
        time.sleep(2) #add a lag to allow python execute your trade
        log_message(f'Sold {max(1,quantity(trade_decision.symbol))} stocks in {trade_decision.symbol}')
        try:
            filled_qty = api_client.get_open_position(trade_decision.symbol).qty 
            time.sleep(1)
            trailing_order = TrailingStopOrderRequest(symbol=trade_decision.symbol, qty=-1*int(filled_qty), side=OrderSide.BUY, time_in_force=TimeInForce.DAY, trail_percent=1.5)
            api_client.submit_order(trailing_order)
            return {
            "entry_order": order,
            "trailing_order": trailing_order,
            "symbol": trade_decision.symbol}
        except Exception as e:
            log_error(e)
            return None

def place_trade(trade_decision:TradeDecision, api:AlpacaApi,api_client:TradingClient, log_message, log_error):
    ot = trade_is_open(trade_decision.symbol, api)
    if ot is not None:
        log_message(f"failed to place trade {trade_decision}, already open: {ot}", trade_decision.symbol)
        return None
    #if there are no open trades or if its none, place a trade
    trade_i = take_trade(trade_decision, api, log_message, log_error)

    if trade_i is None:
        log_error(f"ERROR placing {trade_decision}")
        log_message(f"ERROR placing {trade_decision}", trade_decision.symbol)
        
    else:
        log_message(f"placed trade_id:{trade_i} for {trade_decision}", trade_decision.symbol)
