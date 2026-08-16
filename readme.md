# INVESTBOT_TERMINAL_v1.0

ok so this is my stock tracker thing. i started with streamlit cuz thats what the tutorial said to use but then the ship people said "no streamlit allowed" so i had to rebuild the whole thing in plain html/js which was pain

## what it does

tracks 20 indian stocks. shows prices (fake ones cuz yfinance breaks on github pages). you can buy/sell shares with fake money (₹1L to start). theres charts and some technical indicator stuff i copied from a tutorial (rsi, macd, bollinger, golden/death cross).

## the yolo button

i added a "buy everything" button cuz i thought it would be funny. it buys 1 of each stock, then 2, then 3, until ur broke. i called it yolo mode. my friend said its dumb but i kept it anyway.

## why i built this

i wanted to learn how stocks work without losing real money. also i got scammed by a stock tips whatsapp group in 2024 (not rly scammed just lost money on bad tips) so i decided to actually understand this stuff instead of listening to random people.

## the painful parts

- **tata motors symbol**: i spent like 3 hours trying to figure out why `TATAMOTORS.NS` didnt work. turns out its `TMCV.NS` on yahoo finance. who named this stuff??
- **streamlit got rejected**: i had a working streamlit app with a live link and everything. then they said "no streamlit, use github pages." so i had to throw away all the python and rewrite everything in javascript which i barely know
- **the .ilox bug**: i kept typing `.ilox` instead of `.iloc` and couldnt figure out why my technical indicators were broken for like an hour. felt really dumb when i found it
- **chart too tall**: the chart kept growing forever and i didnt know why. fix was just putting it in a div with fixed height lol
- **dark mode**: i made it look like a crt terminal cuz i thought it looked cool. green phosphor + scanlines. theres also an amber mode if u click the button

## how to run

just open `index.html` in a browser. or put it on github pages. no install needed cuz its just html.

data saves to localStorage so it persists between refreshes (unless u clear ur browser data then its gone lol).

## live demo

(https://hertty15.github.io/The-Watcher/)

## known issues

- prices are fake and randomly generated. they wiggle around to look alive
- on the live demo link ur data saves to ur browser only. if u close the tab and come back on a different device its gone
- mobile probably looks bad. i didnt rly test it
- the rsi/macd math might be wrong. i copied it from stackoverflow and it seems to work but idk

## disclaimer

this is just for learning. not financial advice. if u lose real money thats on u.

---

last updated: aug 2026
