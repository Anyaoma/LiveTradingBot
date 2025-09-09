# Live Trading Bot
This project implements a fully automated live 24/7 trading bot capable of executing strategies in equities; more or less a plug and play strategy integration, that can trade any number of instruments in parrallel.

<img width="1400" height="933" alt="image" src="https://github.com/user-attachments/assets/8117ecda-ac6a-41d2-93c1-0ffd638a5403" />

## Introduction

The bot integrates data acquisition, strategy logic, risk management, error log, and execution into a single framework, aiming to optimize trading performance and reduce manual intervention.

## Motivation / Background

This project was built to:

- Automate a trading strategy with precision that can run 24/7

- Provide real-time monitoring and execution using log files

- Enable scalability across multiple assets

## How the Bot works
- The Bot will be started, and it will create some log files that will be used to log information on each asset.
- The Bot enters an infinite loop, where it loads some candles from the Alpaca API and asks; "Do we have a new candle?"
- If there is indeed a new candle, it will try to identify from the loaded candles a trading signal.
- If there is indeed a trading signal, it's then going to ask; "Can I place a trade?". Under the hood, the bot can confirm if conditions are right to actually place a trade. For example, if the plan is to avoid placing multiple trades on a single asset, the bot will confirm that there isn't a position running on that asset.
- If it is confirmed that a trade can be placed, then the bot places a trade.
- If any of the conditions above don't align, the bot sleeps for a few seconds before loading another set of candles and repeating the cycle as detailed above.

## Bot Structure / Architecture

In terms of the structure of the bot, there is the bot class thats going to contain a candle manager class, a technical class, and a trade manager class. 

The bot class will have the log files set up. 

The candle manager class answers the query "Do we have a new candle?" It will load up the candle, process them and answer the question of whether there is a new candle.

The technicals manager class answers the query "Do we have a signal?". To illustrate, if there is a new candle, we pass the candles we loaded from the candle manager class, and the Technicals class will identify the signals.

The trade manager class answers the question "Can we trade?" by ensuring conditions are accurate to trade, and finally, if it can, it will then place the trade.

<pre> Bot-----|
                    
+------------------+
|  Candle Manager  |
+------------------+
          |
          v
+--------------------+
| Technicals Manager |
+--------------------+
          |
          v
+------------------+
| Trade Manager    |
+------------------+

  </pre>

## Strategy Overview

This strategy combines the MACD indicator with the Stochastic Oscillator to identify high-probability reversal points. The goal is to trade when momentum shifts occur at market extremes.

Indicators Used

- MACD (Moving Average Convergence Divergence): Tracks momentum by comparing the difference between short- and long-term EMAs. A crossover between the MACD line and its Signal line indicates a potential trend reversal.

- Stochastic Oscillator (%K): Measures the current price relative to its range over a lookback period. Used here to detect overbought (>80) and oversold (<20) conditions.

## Entry Rules

#### Buy (Long) Signal:

MACD line crosses above its Signal line (bullish crossover).

Previous MACD was below the Signal line.

Stochastic indicates the market is oversold (<20).


#### Sell (Short) Signal:

MACD line crosses below its Signal line (bearish crossover).

Previous MACD was above the Signal line.

Stochastic indicates the market is overbought (>80).


#### Exit Rules

Once a trade is entered, the bot automatically places a trailing stop order to protect profits and limit losses:

For Long Positions (BUY): 
- A trailing stop sell order is placed at 1.5% below the highest price reached after entry.
- If the price rises, the stop price moves up with it.
- If the price falls more than 1.5% from its peak, the position is closed.

For Short Positions (SELL):
- A trailing stop buy order is placed at 1.5% above the lowest price reached after entry.
- If the price drops, the stop price follows down.
- If the price rises more than 1.5% from its lowest point, the position is closed.

This ensures the bot locks in gains while capping downside risk, without needing constant manual monitoring. 

## How to Run

Clone the repository:

```bash
git clone https://github.com/Anyaoma/quant-tech-bot.git
cd quant-tech-bot

Install dependencies:

pip install -r requirements.txt

Start live trading:
python live_trade.py --strategy momentum_trend
