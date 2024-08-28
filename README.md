# - MAS Algo-Trading Bot - IS5006 Project

A Multi Agent System Trading Bot to maintain an active portfolio of BTC on a paper trading platform.

## How To Start

Install the relevant packages using the following command:
`pip install -r requirements.txt`

The simulation can be run with the command:
`python simulate.py`

Start the live trading bot using the following command:
`python start.py`

## Data

Historic OHLCV data is scraped for the past 1 year to use to train the model. 
The model is run live on minute level data to make decisions and trade with automated API calls.

## Algorithm

Ensemble models are trained over the historic data that leverage multiple technical indicators to calculate directions of price movements.

The technical indicators used include:

- Bollinger Bands
- RSI
- Sentiment Analysis
- Value at Risk
- Macroeconomic Data

With the model outputs for the direction of movement, a dynamic mathemtical model is setup with a weighted basis to calculate the potential to BUY/SELL the asset at every tick.

Live prices are fetched at every tick to assess past trade actions made and make online weight updates to the model creating a robust algorithm across market conditions.

## Monitoring

A PowerBI dashboard is also set up concurrently, which is pinged at every tick to monitor the algorithm performance, decision making ability and model weights.

## Group Members

| Name               | Student ID |
| ------------------ | ---------- |
| Shubhankar Agrawal | A0248330L  |
| Ding Yi Xin        | A0027308L  |
| Ryan Wong          | A0242113Y  |
| Varsha Singh       | A0232471M  |
