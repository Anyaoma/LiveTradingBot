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


