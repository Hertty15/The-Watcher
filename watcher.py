import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import random
import time
from datetime import datetime

#-save data to the file-
#making a json to store data. lol didnt know abt this
SAVE_FILE="my_portfolio.json"
def load_stuff():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    #first time running give ₹1k
    return{
        "cash": 100000.0,
        "portfolio": {},
        "transactions": [],
        "alerts":[],
        "watchlist": ["TMCV.NS", "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ZOMATO.NS"]
    }

def save_stuff(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)

#load it into session_state sp streamlit can remember
if "data" not in st.session_state:
    st.session_state.data =load_stuff()

#doing this so i dont hv to type the whole st.session_state.data eac time
d=st.session_state.data

#--all the stocks we will hv--
#expanded the amount of stocks

ALL_STOCKS={
    "TMCV.NS": "Tata Motors",
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "INFY.NS": "Infosys",
    "HDFCBANK.NS": "HDFC Bank",
    "ZOMATO.NS": "Zomata",
    "SBIN.NS": "State Bank of India",
    "BHARTIARTL.NS": "Bharti Airtel",
    "WIPRO.NS": "Wipro",
    "ADANIENT.NS": "Adani Enterprises",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "ICICIBANK.NS": "ICICI Bank",
    "AXISBANK.NS": "Axis Bank",
    "ITC.NS": "ITC",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "LT.NS": "Larsen and Toubro",
    "MARUTI.NS": "Maruti Suzuki",
    "SUNPHARMA.NS": "Sun Pharma",
    "BAJFINANCE.NS": "Bajaj Finance",
    "ASIANPAINT.NS": "Asian Paints"
}

#make sure every stock has an entry in the portfolio starting at 0
for sym in ALL_STOCKS:
    if sym not in d["portfolio"]:
        d["portfolio"][sym]=0

#---demo mode---
#yfinance smtimse breaks on streamlit cloud so made this so ppl can still try out the project even if they rnt seeeing current data

DEMO_PRICES= {
    "TMCV.NS": 445.00,
    "RELIANCE.NS": 1293.00,
    "TCS.NS":2452.00,
    "INFY.NS":1158.00,
    "HDFCBANK.NS":739.00,
    "ZOMATO.NS":280.00,
    "SBIN.NS":620.00,
    "BHARTIARTL.NS": 1680.00,
    "WIPRO.NS":285.00,
    "ADANIENT.NS":2450.00,
    "HINDUNILVR.NS":2450.00,
    "ICICIBANK.NS":1280.00,
    "AXISBANK":980.00,
    "ITC.NS":430.00,
    "KOTAKBANK":1780.00,
    "LT.NS":3580.00,
    "MARUTI.NS":11200.00,
    "SUNPHARMA.NS":1780.00,
    "BAJFINANCE":6850.00,
    "ASIANPAINTS.NS":2350.00
}

#fake yest prices -- randomised a bit
random.seed(42) #so its consistenn
DEMO_PREV={k:round(v*random.uniform(0.985, 1.015), 2) for k, v in DEMO_PRICES.items()}

def get_demo_price(symbol):
    base=DEMO_PRICES.get(symbol, 500)
    wiggle=random.uniform(-1.5, 1.5)
    return round(base + wiggle, 2)

def get_demo_yest(symbol):
    return DEMO_PREV.get(symbol, 500)

def get_demo_chart(symbol, period="1mo"):
    base=DEMO_PRICES.get(symbol, 500)
    if period=="1d":
        points=60
        noise=np.random.normal(0, 0.4, points)
        trend=np.linspace(base -4, base, points)
        freq="min"
    elif period=="1wk":
        points=7
        noise=np.random.normal(0,3, points)
        trend=np.linspace(base*0.97, base, points)
        freq="D"
    elif period =="3mo":
        points=90
        noise=np.random.normal(0,12, points)
        trend=np.linspace(base*0.88, base, points)
        freq="D"
    else: #default is 1mo
        points=30
        noise= np.random.normal(0,6, points)
        trend= np.linspace(base *0.93, base, points)
        freq="D"

    prices_arr=trend+noise
    dates= pd.date_range(end= datetime.now(), periods=points, freq=freq)
    return pd.DataFrame({"Close": prices_arr}, index=dates)

#----streamlit page setup
st.set_page_config(page_title="InvestBot", page_icon="💸", layout="wide")

st.markdown("""
<style>
    .main-title{font-size: 2.2rem; font-weight:800;}
    .subtitle{color: #6b7280; font-size: 1rem; margin-bottom: 1.5rem}
    div[data-testid="stMetricValue"] {font-size: 1.5rem !important; font-weight: 700 !important;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">InvestBot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Indian stocks, paper trading, and fake money so u dont go broke using acc money</div>', unsafe_allow_html=True)

#sidebar stuff
st.sidebar.title("Settings")
demo_mode=st.sidebar.toggle("Demo Mode (fake data)", value=True)

if demo_mode:
    st.sidebar.info("Demo Mode ON - using simulated prices", icon="💸")

st.sidebar.divider()

#add stocks to watchlist
st.sidebar.subheader("Add Stock")
not_watching=[s for s in ALL_STOCKS if s not in d["watchlist"]]
if not_watching:
    pick=st.sidebar.selectbox("Pick a stock", not_watching, format_func=lambda x:f"{ALL_STOCKS[x]} ({x})")
    if st.sidebar.button("Add to Watchist", use_container_width=True):
        d["Watchlist"].append(pick)
        save_stuff(d)
else:
    st.sidebar.caption("u can watch everything.")

st.sidebar.divider()

#price alerts
st.sidebar.subheader("Price Alerts")
alert_sym=st.sidebar.selectbox("Stock", d["watchlist"], format_func= lambda x:ALL_STOCKS[x], key="alert_sym")
alert_dir=st.sidebar.radio("Alert when", ["goes above", "goes below"], horizontal=True, key="alert_dir")
alert_price=st.sidebar.number_input("Price (Rs)", min_value=1.0, value=1000.0, step=10.0, key="alert_price")

if st.sidebar.button("Set Alert", use_container_width=True):
    d["alerts"].append({
        "symbol": alert_sym,
        "direction": alert_dir,
        "target": alert_price,
        "set_time": datetime.now().strftime("%d %b %H:%M")
    })
    save_stuff(d)
    st.sidebar.success(f"Alert set!")

#show active alerts
if d["alerts"]:
    st.sidebar.divider()
    st.sidebar.subheader("Your Alerts")
    for i, alert in enumerate(d["alerts"]):
        c1, c2 =st.sidebar.columns([4,1])
        with c1:
            st.sidebar.caption(f"{ALL_STOCKS[alert['symbol']]} {alert['direction']} Rs{alert['target']:.2f}")
        with c2:
            if st.sidebar.button("X", key=f"del_alert_{i}"):
                d["alerts"].pop(i)
                save_stuff(d)
                st.rerun()

st.sidebar.divider()
st.sidebar.caption("danger Zone")
if st.sidebar.button("Reset Everything", use_container_width=True):
    d["cash"]=100000.0
    d["portfolio"]={s: 0 for s in ALL_STOCKS}
    d["transactions"]=[]
    d["alerts"]=[]
    save_stuff(d)
    st.rerun()

#-----fetch prices
prices={}
yest={}

for symbol in d["watchlist"]:
    if demo_mode:
        prices[symbol]=get_demo_price(symbol)
        yest[symbol]= get_demo_yest(symbol)
    else:
        try:
            hist=yf.Ticker(symbol).history(period="5d", interval="1d")
            prices[symbol]=float(hist["Close"].iloc[-1])
            yest[symbol]=float(hist["Close"].iloc[-2])
            time.sleep(0.2) #dont spam the api
        except Exception as e:
            #fallback to demo if api fails
            prices[symbol]=get_demo_price(symbol)
            yest[symbol]=get_demo_yest(symbol)

#check alerts and toast if triggered
for sym, price in prices.items():
    triggered=[]
    remaining=[]
    for alerts in d["alerts"]:
        if alert["symbol"] ==sym:
            if alert["direction"]=="goes above" and price >= alert["target"]:
                triggered.append(alert)
            elif alert["direction"]=="goes below" and price <= alert["target"]:
                triggered.append(alert)
            else:
                remaining.append(alert)
        else:
            remaining.append(alert)

    d["alerts"]=remaining
    for t in triggered:
        st.toast(f"ALERT: {ALL_STOCKS[t['symbol']]} is {t['direction']} Rs{t['target']:.2f}!")
        triggered=True

if triggered:
    save_stuff(d)

#------portfolio summary------
#calc total val=cash+ all stcosk u won

total_val= d["cash"]
for sym, qty in d["portfolio"].items():
    total_val += qty*prices.get(sym, 0)

invested= total_val - d["cash"]
profit_loss= total_val-100000.0
profit_loss_pct= (profit_loss/ 100000.0) *100

c1, c2, c3, c4=st.columns(4)
with c1:
    st.metric("Cash", f"Rs{d['cash']:.2f}")
with c2:
    st.metric("Invested", f"Rs{invested:,.2f}")
with c3:
    st.metric("Total Value", f"Rs{total_val:,.2f}")
with c4:
    st.metric("P&L (vs Rs1L start)", f"Rs{profit_loss:+.2f}", delta=f"{profit_loss_pct:+.2f}%")

st.divider()

#-------charts-------
st.subheader("Charts & Signals")

chart_stock=st.selectbox("Pick a stock to chart", d["watchlist"], format_func=lambda x:ALL_STOCKS[x])
timeframe=st.radio("Timeframe", ["1D","1W","1M","3M"], horizontal=True)

if demo_mode:
    if timeframe=="1D":
        chart_df=get_demo_chart(chart_stock, "1d")
    elif timeframe=="1W":
        chart_df=get_demo_chart(chart_stock, "1wk")
    elif timeframe == "3M":
        chart_df=get_demo_chart(chart_stock, "3mo")
    else:
        chart_df=get_demo_chart(chart_stock, "1mo")
else:
    try:
        if timeframe=="1D":
            chart_df=yf.Ticker(chart_stock).history(period="1d", interval="5m")
        elif timeframe=="1W":
            chart_df=yf.Ticker(chart_stock).history(period="1wk", interval="1h")
        elif timeframe=="3M":
            chart_df=yf.Ticker(chart_stock).history(period="3mo", interval="1d")
        else:
            chart_df=yf.Ticker(chart_stock).history(period="1mo", interval="1d")
    except:
        chart_df=pd.DataFrame()

#show the chart
if not chart_df.empty:
    st.line_chart(chart_df["Close"])
else:
    st.write("No chart data available")

#techniacl indicators
st.caption("Technical Signals")

#get 60 days of data for indicators
if demo_mode:
    ind_df=get_demo_chart(chart_stock, "3mo")
else:
    try:
        ind_df=yf.Ticker(chart_stock).history(period="3mo", interval="1d")
    except:
        ind_df=pd.DataFrame()

if not ind_df.empty:
    close=ind_df["Close"]

    #moving averages (ma)
    ma20=close.rolling(window=20).mean()
    ma50=close.rolling(window=50).mean()

    #RSI (relative strength index)-tells if stock is overbought/oversold
    delta=close.diff()
    gain=delta.where(delta >0, 0).rolling(window=14).mean()
    loss= (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs=gain / loss
    rsi= 100 -(100 / (1+ rs))
    latest_rsi=float(rsi.dropna().iloc[-1]) if not rsi.dropna().empty else 50

    #macd
    ema12= close.ewm(span=12, adjust=False).mean()
    ema26= close.ewm(span=26, adjust=False).mean()
    macd= ema12 - ema26
    macd_signal=macd.ewm(span=9, adjust=False).mean()
    latest_macd=float(macd.dropna().iloc[-1]) if not macd.dropna().empty else 0
    latest_signal= float(macd_signal.dropna().iloc[-1]) if not macd_signal.dropna().empty else 0

    #bollinger bands
    ma20_bb= close.rolling(window=20).mean()
    std20= close.rolling(window=20).std()
    upper_bb= ma20_bb + (std20 * 2)
    lower_bb= ma20_bb - (std20 * 2)
    latest_price= float(close.iloc[-1])
    latest_upper= float(upper_bb.dropna().iloc[-1]) if not upper_bb.dropna().empty else latest_price
    latest_lower= float(lower_bb.dropna().iloc[-1]) if not lower_bb.dropna().empty else latest_price

    #golden/death cross
    latest_ma20= float(ma20.dropna().iloc[-1]) if not ma20.dropna().empty else 0
    latest_ma50= float(ma50.dropna().iloc[-1]) if not ma50.dropna().empty else 0

    #display signals in columns
    sig1, sig2, sig3, sig4=st.columns(4)

    with sig1:
        if latest_ma20>latest_ma50:
            st.success("Golden Cross - BUY")
        elif latest_ma20<latest_ma50:
            st.error("Death Cross - SELL")
        else:
            st.info("Neutral - HOLD")

    with sig2:
        if latest_rsi>70:
            st.error(f" RSI {latest_rsi:.1f} - Overbought")
        elif latest_rsi<30:
            st.success(f" RSI {latest_rsi:.1f} - Oversold")
        else:
            st.info(f" RSI {latest_rsi:.1f} - Normal")

        with sig3:
            if latest_macd>latest_signal:
                st.success("MACD  is  Bullish")
            else:
                st.error("MACD is Bearish")

        with sig4:
            if latest_price>latest_upper:
                st.error("Above Bollinger - Overbought")
            elif latest_price<latest_lower:
                st.success(" Below Bollinger - Oversold")
            else:
                st.info("Inside Bollinger Band")

st.divider()

#--------stock cards grid--------
st.subheader("Watchlist")

#3 columns grid
cols= st.columns(3)

for i, symbol in enumerate(d["watchlist"]):
    with cols[1 % 3]:
        price=prices.get(symbol, 0)
        prev=yest.get(symbol, 0)
        change=price - prev
        change_pct=(change/prev) * 100 if prev != 0 else 0
        shares = d["portfolio"].get(symbol,0)

        #color the card border based on profit or loss (up/down)
        border_color= "#10b981" if change >=0 else "#ef4444"

        st.markdown(f"""
        <div style="border: 2px solid {border_color}; border-radius: 12px; padding:1rem; margin-bottom:1rem; background: #ffffff;">
            <div style="font-weight: 700; font-size: 1.1rem;">{ALL_STOCKS[symbol]}</div>
            <div style="color: #6b7280; font-size: 0.85rem;">{symbol}</div>
        """, unsafe_allow_html=True)

        #metric
        delta_str= f"Rs{abs(change):.2f} ({abs(change_pct):.2f}%)"
        st.metric(label="", value=f"Rs{price:.2f}", delta=f"{'+' if change >=0  else '-'}{delta_str}")

        st.caption(f"You own: {shares} shares (Rs{shares * price:,.2f})")

        #buy/sell with quantity
        bcol1, bcol2 = st.columns(2)
        with bcol1:
            qty_buy=st.number_input("Qty", min_value=1, max_value=100, value=1, key=f"but qty {symbol}", label_visibility="collapsed")
            if st.button("Buy", key=f"buy_{symbol}", use_container_width=True):
                total=qty_buy*price
                if d["cash"] >= total:
                    d["cash"] -= total
                    d["portfolio"][symbol] +=qty_buy
                    d["transactions"].insert(0, {
                        "time": datetime.now().strftime("%d %b %H:%M"),
                        "action": "BUY",
                        "symbol": symbol,
                        "name": ALL_STOCKS[symbol],
                        "qty": qty_buy,
                        "price": round(price,2),
                        "total": round(total,2)
                    })
                    save_stuff(d)
                    st.rerun()
                else:
                    st.error("Not enough cash!", icon="💸")
        with bcol2:
            qty_sell= st.number_input("Qty", min_value=1, max_value=d["portfolio"].get(symbol,0) or 1, value=1, key=f"se;;_qty_{symbol}", label_visibility="collapsed")
            if st.button("Sell", key=f"sell_{symbol}", use_container_width=True):
                if d["portfolio"].get(symbol, 0) >=qty_sell:
                    total+qty_sell * price
                    d["cash"] += total
                    d["portfolio"][symbol] -= qty_sell
                    d["transactions"].insert(0, {
                        "time": datetime.now().strftime("%d %b %H:%M"),
                        "action": "SELL",
                        "symbol": symbol,
                        "name":ALL_STOCKS[symbol],
                        "qty": qty_sell,
                        "price": round(price, 2),
                        "total": round(total, 2)
                    })
                    save_stuff(d)
                    st.rerun()
                else:
                    st.error("You dont own many.", icon="💸")

        st.markdown("</div>", unsafe_allow_html=True)

#---------transaction history---------
st.divider()
st.subheader("Transaction History")

if not d["transactions"]:
    st.caption("No trades yet. Go buy something!")
else:
    #show last 20 transaxtions in a table
    recent= d["transactions"][:20]

    for txn in recent:
        color= "#10b981" if txn["action"] == "BUY" else "#ef4444"
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items:center; padding: 0.6rem 1rem; background: #f9fafb; border-radius: 8px; margin-bottom: 0.4rem;">
            <div>
                <span style="color: {color}; font-weight: 700;">{txn['action']}</span>
                <spn style="margin-left: 0.5rem;">{txn['qty']} x {txn['name']}</span>
            </div>
            <div style="text-align: right;">
                <div style="font-weight: 600;">Rs{txn['total']:,.2f}</div>
                <div style="color: #9ca3af; font-size: 0.8rem;">{txn['time']} @ Rs{txn['price']:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

#----------footer----------
st.divider()
st.caption("IvestBot - built for learning. Not financial advice. Pls dont sue me")