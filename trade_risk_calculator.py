from oanda_api.Oanda_api import OandaApi
import constants.defs as defs
from instruments.instruments_data import instrumentCollection as ic


def get_trade_units(api:OandaApi, pair, signal, loss, trade_risk, log_message):

    prices = api.get_prices([pair])
    if prices is None or len(prices) == 0:
        log_message(f"get_trade_units() prices is none", pair)
        return False #we'll use True or false to indicate to the caller whether things have worked or not

    price = None
    for p in prices:
        if p.instrument == pair:
            price = p
            break
    if price == None:
        log_message(f"get_trade_units() prices is none???", pair)
        return False
    
    log_message(f"get_trade_units() price {price}", pair)

    conv = price.buy_conv
    if signal == defs.SELL:
        conv = price.sell_conv

    pipLocation = ic.instrument_dict[pair].pipLocation
    num_pips = loss / pipLocation #number of pips we've lost/gonna be loosing
    #amount we are prepared to lose per pip
    per_pip_loss = trade_risk / num_pips
    #units that represent the amount we gonna lose per pip
    units = per_pip_loss / (conv*pipLocation)

    log_message(f"{pipLocation} {num_pips} {per_pip_loss} {units:.1f}", pair)

    return units
