# InvestBot 🤖

hey! this is InvestBot — an investment dashboard i built that tracks Indian stocks, shows live prices, and even lets you paper trade (fake money so u dont go broke lol).

## what it does

- tracks 20 Indian stocks now (started with 6 but got carried away)
- shows prices, daily change, and if the stock is up or down
- chart with 1D / 1W / 1M / 3M views
- some technical signal stuff:
  - Golden Cross / Death Cross (20-day vs 50-day MA) — this one i actually understand
  - RSI — tells if stock is overbought/oversold. idk how the math works but the numbers look right
  - MACD — bullish/bearish thing. copied from a tutorial. seems legit
  - Bollinger Bands — apparently if price goes outside the bands its "extreme". ok sure
- buy/sell multiple shares at once (old version only let u buy 1 at a time which was annoying)
- starts with Rs 1,00,000 fake cash (10k felt too low lol)
- **saves ur portfolio to a json file** so it doesnt vanish when u refresh (this took me way too long to figure out)
- transaction history so u can see every dumb trade u made
- price alerts — set a target and it yells at u when the stock hits it
- add/remove stocks from watchlist
- reset button for when u blow all ur money on zomato

## why i built this

i wanted to learn how the stock market works and also learn Python. turns out getting stock data is WAY harder than i thought. i spent like 3 days just trying to get the API to work because every library was broken or blocked.

the hardest part was figuring out that Tata Motors' Yahoo Finance symbol is "TMCV.NS" not "TATAMOTORS.NS" 😭 that took forever.

this version is way bigger than my first one. i added json saving (so ur portfolio actually stays), price alerts, more stocks, and technical indicators. i still dont fully understand RSI and MACD but i copied the math from a tutorial and it seems to work lol.

also i kept typing `.ilox` instead of `.iloc` and couldnt figure out why it was broken for like an hour. classic.

## live demo

try it here without installing anything:  
https://the-watcher-hqndp6epbu5s9rywgqvo8m.streamlit.app/

**note:** the demo uses fake prices that wiggle around. also on the live link, your portfolio resets when u close the tab (cloud cant save files). download and run locally if u want it to actually remember your trades.

## how to run it locally (for real live data)

```bash
pip install -r requirements.txt
streamlit run watcher.py