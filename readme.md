# InvestBot 🤖

hey! this is InvestBot — an investment dashboard i built that tracks Indian stocks, shows live prices, and even lets you paper trade (fake money so you dont go broke lol).

## what it does

- tracks 6 Indian stocks: Tata Motors, Reliance, TCS, Infosys, HDFC Bank, Zomato
- shows prices, daily change, and if the stock is up or down
- has a chart where you can switch between 1 day and 1 month view
- has a "Golden Cross / Death Cross" signal — its a real trading strategy that checks if the 20-day moving average is above or below the 50-day one
- you can buy and sell shares with fake money (₹10,000 to start)
- tracks your portfolio value in real time

## why i built this

i wanted to learn how the stock market works and also learn Python. turns out getting stock data is WAY harder than i thought. i spent like 3 days just trying to get the API to work because every library was broken or blocked. 

the hardest part was figuring out that Tata Motors' Yahoo Finance symbol is "TMCV.NS" not "TATAMOTORS.NS" 😭 that took forever.

## how to run it locally (for real live data)

if you want to see ACTUAL live market data:

```bash
pip install -r requirements.txt
streamlit run dashboard.py