import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import constants.constants as defs


import requests
  # assuming defs.py contains your api_url and SECURE_HEADER

class AlpacaApi:
    def __init__(self):
        self.name = 'AlpacaApi'
        self.base_url = defs.api_hist_url
        self.headers = defs.SECURE_HEADER

    def make_requests(self, url, verb='GET', code=200, params=None, json=None):
        full_url = f'{self.base_url}/{url}'
        try:
            response = None
            if verb == 'GET':
                response = requests.get(full_url, params=params, headers=self.headers)

            if verb == 'POST':
                response = requests.post(full_url, json=json, headers=self.headers)
            
            if response == None:
                return False, {'error': 'verb not found'}

            if response.status_code == code:
                try:
                    return True, response.json()
                except ValueError:
                    return True, response.text
            else:
                return False, response.json()

        except Exception as error:
            return False, {'Exception': str(error)}

    def fetch_bars(self, symbols, time_frame='5Min', limit=1000, start=None, end=None):
        url = 'v2/stocks/bars' 
        params = {
            'symbols': ','.join(symbols) if isinstance(symbols, list) else symbols,
            'timeframe': time_frame,
            'limit': limit,
            'feed': 'iex'}

        # Optionally add start and end times if provided
        if start:
            params['start'] = start
        if end:
            params['end'] = end

        all_bars = {}
        next_page_token = None
        while True:
            if next_page_token:
                params['page_token'] = next_page_token

            ok, data = self.make_requests(url, params=params, verb='GET')
            if not ok:
                print('ERROR fetch_bars()', params, data)
                return None
            #merge bars into all_bars
            bars = data.get('bars',{}) #return bars, if not found, return an empty list
            for symbol, bar_data in bars.items():
                all_bars.setdefault(symbol, []).extend(bar_data)

            #check for next_page_token
            next_page_token = data.get('next_page_token')
            if not next_page_token:
                break #no more pages, exit loop
        #print(all_bars)
        return all_bars
        
    def fetch_df(self, symbols, time_frame='4H', limit=1000, start=None, end=None):
        '''
        returns historical data for selected assets and time period
        '''
        df_data = {}
        data = self.fetch_bars(symbols=symbols,time_frame=time_frame, limit=limit, start=start, end=end)

        if data:
            for symbol in data:
                new_data = pd.DataFrame(data[symbol])
                new_data.rename({'t':'time','o':'open','c':'close','h':'high','l':'low','v':'volume'},axis=1, inplace=True)
                new_data['time'] = pd.to_datetime(new_data['time'])
                new_data.set_index('time', inplace=True)
                new_data.index.tz_convert('Europe/London')
                new_data.between_time("09:31", "16:00")
                df_data[symbol] = new_data
            #print(df_data)
            return df_data 
        else:
            print('code returned none')
            return None
        
    def fetch_latest_bar(self, symbol):
        url = f'v2/stocks/bars/latest'
        params = dict(symbols=symbol, feed = 'iex')
        ok, data = self.make_requests(url, params=params, verb='GET')

        if ok:
            print(data)
        else:
            return False, {'error occured'}
        
    def place_mkt_order(self, symbol, qty, side, time_in_force='day'):
        url = "v2/orders"
        params = dict(symbol=symbol, qty=qty,side=side,order_class= "simple",
                     type='market', time_in_force=time_in_force)
        ok, data = self.make_requests(url, verb='POST',json=params)
        if not ok:
            return False, {'code returned no data'}
        print(data)
        #return data
    
    
    def place_lmt_order(self, symbol, qty, side,limit_price, time_in_force='day'):
        url = "v2/orders"
        params = dict(symbol=symbol, qty=qty,side=side,
                      limit_price=limit_price,order_class= "simple",
                     type='limit', time_in_force=time_in_force)
        ok, data = self.make_requests(url, verb='POST',json=params)
        if not ok:
            return False, {'code returned no data'}
        print(data)
        #return data
    
    def mkt_plus_stop_loss(self, symbol, qty, side, take_profit, stop_loss ,order_class='bracket', time_in_force='day'):
        url = "v2/orders"
        params = dict(symbol=symbol, qty=qty, side=side, stop_loss={'stop_price':stop_loss},
                     type='market',take_profit={'limit_price':take_profit},
                       order_class=order_class, time_in_force=time_in_force)

        ok, data = self.make_requests(url, verb='POST',json=params)
        if not ok:
            return False, {'code returned no data'}
        print(data)
        #return data
    
    def take_profit_order(self, symbol, qty, side,limit_price, time_in_force='day'):# the side would be the opposite of the market order
        url = "v2/orders"
        params = dict(symbol=symbol, qty=qty,side=side,order_class= "simple",
                     type='limit',limit_price=limit_price, time_in_force=time_in_force)
        ok, data = self.make_requests(url, verb='POST',json=params)
        if not ok:
            return False, {'code returned no data'}
        print(data)
        #return data
        
    def trailing_stop(self, symbol, qty, side, trail_percent='2',order_class='simple', time_in_force='day'):
        url = "v2/orders"
        params = dict(symbol=symbol, qty=qty,side=side,trail_percent=trail_percent,
                     type='trailing_stop', order_class=order_class,time_in_force=time_in_force)
       
        ok, data = self.make_requests(url, verb='POST',json=params)
        if not ok:
            return False, {'code returned no data'}
        print(data)
        #return data

    def last_complete_candle(self, symbol, time_frame='15Mins', limit=10, start=None, end=None ):
        data = self.fetch_df(symbols=symbol,time_frame=time_frame, limit=limit)
        if data.shape[0] == 0:
            return None
        return data[symbol]['time'].iloc[-1]
