import streamlit as st
import yfinance as yf
import random
import time

# ============================================
# SECTION 1: BACKPACK
# ============================================
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {
        "TMCV.NS": 0,
        "RELIANCE.NS": 0,
        "TCS.NS": 0,
        "INFY.NS": 0,
        "HDFCBANK.NS": 0,
        "ZOMATO.NS": 0
    }
    st.session_state.cash = 10000

# ============================================
# SECTION 2: DEMO MODE SETUP
# ============================================
st.sidebar.title("⚙️ Settings")
demo_mode = st.sidebar.toggle("Demo Mode (Cloud-friendly)", value=True)

# Base prices for demo mode (realistic approximations)
DEMO_PRICES = {
    "TMCV.NS": 445.00,
    "RELIANCE.NS": 1293.00,
    "TCS.NS": 2452.00,
    "INFY.NS": 1158.00,
    "HDFCBANK.NS": 739.00,
    "ZOMATO.NS": 280.00
}

# Previous day prices for demo mode (slightly different)
DEMO_PREVIOUS = {
    "TMCV.NS": 452.50,
    "RELIANCE.NS": 1317.00,
    "TCS.NS": 2472.00,
    "INFY.NS": 1170.00,
    "HDFCBANK.NS": 753.00,
    "ZOMATO.NS": 285.00
}

def get_demo_price(symbol):
    """Returns a wiggling demo price so it looks alive"""
    base = DEMO_PRICES.get(symbol, 100)
    wiggle = random.uniform(-0.5, 0.5)  # Moves ±₹0.50
    return round(base + wiggle, 2)

def get_demo_previous(symbol):
    """Returns yesterday's demo price"""
    return DEMO_PREVIOUS.get(symbol, 100)

def get_demo_chart(symbol, period="1mo"):
    """Generates fake chart data for demo mode"""
    import pandas as pd
    import numpy as np
    
    base = DEMO_PRICES.get(symbol, 100)
    
    if period == "1d":
        # 1 day = 60 minute points
        points = 60
        noise = np.random.normal(0, 0.2, points)
        trend = np.linspace(base - 2, base, points)
    else:
        # 1 month = 30 daily points
        points = 30
        noise = np.random.normal(0, 5, points)
        trend = np.linspace(base * 0.95, base, points)
    
    prices = trend + noise
    dates = pd.date_range(end=pd.Timestamp.now(), periods=points, freq="min" if period == "1d" else "D")
    
    df = pd.DataFrame({"Close": prices}, index=dates)
    return df

# ============================================
# SECTION 3: STOCK LIST
# ============================================
stocks = [
    ("TMCV.NS", "Tata Motors"),
    ("RELIANCE.NS", "Reliance Industries"),
    ("TCS.NS", "Tata Consultancy Services"),
    ("INFY.NS", "Infosys"),
    ("HDFCBANK.NS", "HDFC Bank"),
    ("ZOMATO.NS", "Zomato")
]

# ============================================
# SECTION 4: FETCH ALL PRICES
# ============================================
prices = {}
previous_prices = {}

for symbol, name in stocks:
    if demo_mode:
        prices[symbol] = get_demo_price(symbol)
        previous_prices[symbol] = get_demo_previous(symbol)
    else:
        try:
            data = yf.Ticker(symbol).history(period="5d", interval="1d")
            prices[symbol] = float(data["Close"].iloc[-1])
            previous_prices[symbol] = float(yf.Ticker(symbol).info.get("previousClose", data["Close"].iloc[-2]))
            time.sleep(0.3)
        except Exception:
            prices[symbol] = 0
            previous_prices[symbol] = 0

# ============================================
# SECTION 5: CALCULATE PORTFOLIO VALUE
# ============================================
portfolio_value = st.session_state.cash

for symbol, name in stocks:
    shares = st.session_state.portfolio[symbol]
    price = prices[symbol]
    portfolio_value += shares * price

# ============================================
# SECTION 6: DISPLAY PAGE
# ============================================

st.title("InvestBot")

if demo_mode:
    st.sidebar.info("📊 Demo Mode: Using simulated market data")

# Portfolio (compact)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Cash", f"₹{st.session_state.cash:.2f}")
with col2:
    st.metric("Total Shares", sum(st.session_state.portfolio.values()))
with col3:
    st.metric("Portfolio Value", f"₹{portfolio_value:.2f}")

# Chart Section
st.divider()

stock_names = [name for symbol, name in stocks]
chart_name = st.selectbox("📈 Chart this stock:", stock_names)

chart_symbol = None
for symbol, name in stocks:
    if name == chart_name:
        chart_symbol = symbol
        break

timeframe = st.radio("Timeframe:", ["1D", "1M"], horizontal=True)

if chart_symbol:
    if demo_mode:
        chart_data = get_demo_chart(chart_symbol, "1d" if timeframe == "1D" else "1mo")
    else:
        cp = "1d" if timeframe == "1D" else "1mo"
        ci = "1m" if timeframe == "1D" else "1d"
        chart_data = yf.Ticker(chart_symbol).history(period=cp, interval=ci)
    
    if not chart_data.empty:
        st.line_chart(chart_data["Close"])
    else:
        st.write("No chart data available.")

# Moving Average Signal
if chart_symbol:
    if demo_mode:
        # In demo mode, generate a realistic signal based on the stock
        import numpy as np
        demo_60 = get_demo_chart(chart_symbol, "1mo")
        close_60 = demo_60["Close"]
        ma_20 = close_60.rolling(window=20).mean()
        ma_50 = close_60.rolling(window=50).mean()
        
        latest_20 = float(ma_20.dropna().iloc[-1])
        latest_50 = float(ma_50.dropna().iloc[-1])
    else:
        sixty_days = yf.Ticker(chart_symbol).history(period="60d", interval="1d")
        close_60 = sixty_days["Close"]
        ma_20 = close_60.rolling(window=20).mean()
        ma_50 = close_60.rolling(window=50).mean()
        latest_20 = float(ma_20.dropna().iloc[-1])
        latest_50 = float(ma_50.dropna().iloc[-1])
    
    if latest_20 > latest_50:
        st.success(f"🟢 GOLDEN CROSS on {chart_name}: BUY signal!")
    elif latest_20 < latest_50:
        st.error(f"🔴 DEATH CROSS on {chart_name}: SELL signal!")
    else:
        st.info(f"🟡 {chart_name}: HOLD")

st.divider()

# ============================================
# SECTION 7: STOCK CARDS IN GRID
# ============================================

def draw_stock_card(symbol, name):
    today_price = prices.get(symbol, 0)
    yest_price = previous_prices.get(symbol, 0)
    
    if today_price == 0:
        st.metric(label=name, value="N/A", delta="Market data unavailable")
        st.caption("Own: 0 shares")
        b1, b2 = st.columns(2)
        with b1:
            st.button("Buy", key=f"buy_{symbol}", disabled=True)
        with b2:
            st.button("Sell", key=f"sell_{symbol}", disabled=True)
        return
    
    change = today_price - yest_price
    change_pct = (change / yest_price) * 100 if yest_price != 0 else 0
    sign = "+" if change >= 0 else "-"
    
    st.metric(
        label=name,
        value=f"₹{today_price:.2f}",
        delta=f"{sign}₹{abs(change):.2f} ({sign}{abs(change_pct):.2f}%)"
    )
    
    st.caption(f"Own: {st.session_state.portfolio[symbol]} shares")
    
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Buy", key=f"buy_{symbol}"):
            if st.session_state.cash >= today_price:
                st.session_state.cash -= today_price
                st.session_state.portfolio[symbol] += 1
                st.rerun()
            else:
                st.error("No cash!", icon="💸")
    with b2:
        if st.button("Sell", key=f"sell_{symbol}"):
            if st.session_state.portfolio[symbol] > 0:
                st.session_state.cash += today_price
                st.session_state.portfolio[symbol] -= 1
                st.rerun()
            else:
                st.error("No shares!", icon="😢")

cols = st.columns(3)
for i, (symbol, name) in enumerate(stocks):
    with cols[i % 3]:
        draw_stock_card(symbol, name)