# Live Trading Bot
This project implements a fully automated live 24/7 trading bot capable of executing strategies in equities; more or less a plug and play strategy integration, that can trade any number of instruments in parrallel.

<img width="1400" height="933" alt="image" src="https://github.com/user-attachments/assets/8117ecda-ac6a-41d2-93c1-0ffd638a5403" />

## Introduction

The bot integrates data acquisition, strategy logic, risk management, error log, and execution into a single framework, aiming to optimize trading performance and reduce manual intervention.

## Motivation / Background

Manual tradi

## How the Bot works
- The Bot will be started, and it will create some log files that will be used to log information on relevant executions per asset.
- The Bot enters an infinite loop, which involves loading some candles from the Alpaca API and asking; do we have a new candle?
- If there is indeed a new candle, its will try to identify from the loaded candles a trading signal.
- If there is indeed a trading signal, its then going to ask; 'can I place a trade?'. Under the hood the boot could confirm if conditions are right to actually place a trade, e.g if the plan is to avoid placing multiple trades on a single asset, the bot will confirm that there isnt a position running on that asset.
- If it is confirmed that a trade can be placed, then the bot places a trade.
- If any of the conditions above dont align, the bot sleeps for a few seconds before loading another set of candles

