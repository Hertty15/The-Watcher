import streamlit as st
import yfinance as yf

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
# SECTION 2: STOCK LIST
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
# SECTION 3: FETCH ALL PRICES
# ============================================
prices = {}

for symbol, name in stocks:
    try:
        data = yf.Ticker(symbol).history(period="5d", interval="1d")
        prices[symbol] = float(data["Close"].iloc[-1])
    except Exception:
        prices[symbol] = 0

# ============================================
# SECTION 4: CALCULATE PORTFOLIO VALUE
# ============================================
portfolio_value = st.session_state.cash

for symbol, name in stocks:
    shares = st.session_state.portfolio[symbol]
    price = prices[symbol]
    portfolio_value += shares * price

# ============================================
# SECTION 5: DISPLAY PAGE
# ============================================

st.title("InvestBot")

# Portfolio (compact)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Cash", f"₹{st.session_state.cash:.2f}")
with col2:
    st.metric("Total Shares", sum(st.session_state.portfolio.values()))
with col3:
    st.metric("Portfolio Value", f"₹{portfolio_value:.2f}")

# Chart Section with Stock Picker
st.divider()

# Pick which stock to chart
stock_names = [name for symbol, name in stocks]
chart_name = st.selectbox("📈 Chart this stock:", stock_names)

# Find the symbol for the selected name
chart_symbol = None
for symbol, name in stocks:
    if name == chart_name:
        chart_symbol = symbol
        break

# Timeframe picker
timeframe = st.radio("Timeframe:", ["1D", "1M"], horizontal=True)

if timeframe == "1D":
    chart_period = "1d"
    chart_interval = "1m"
else:
    chart_period = "1mo"
    chart_interval = "1d"

# Fetch and show chart
if chart_symbol:
    chart_data = yf.Ticker(chart_symbol).history(period=chart_period, interval=chart_interval)
    if not chart_data.empty:
        st.line_chart(chart_data["Close"])
    else:
        st.write("No chart data available.")

# Moving Average Signal for selected stock
if chart_symbol:
    sixty_days = yf.Ticker(chart_symbol).history(period="60d", interval="1d")
    if not sixty_days.empty:
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
# SECTION 6: STOCK CARDS IN GRID
# ============================================

def draw_stock_card(symbol, name):
    try:
        data = yf.Ticker(symbol).history(period="5d", interval="1d")
        today_price = float(data["Close"].iloc[-1])
        yest_price = float(yf.Ticker(symbol).info.get("previousClose", data["Close"].iloc[-2]))
        
        change = today_price - yest_price
        change_pct = (change / yest_price) * 100
        sign = "+" if change >= 0 else "-"
        
        st.metric(
            label=name,
            value=f"₹{today_price:.2f}",
            delta=f"{sign}₹{abs(change):.2f} ({sign}{abs(change_pct):.2f}%)"
        )
        
        st.caption(f"Own: {st.session_state.portfolio[symbol]} shares")
        
        # Buy/Sell in a compact row
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
                    
    except Exception:
        st.warning(f"Could not load {name}.")

# Draw 3 cards per row
cols = st.columns(3)
for i, (symbol, name) in enumerate(stocks):
    with cols[i % 3]:
        draw_stock_card(symbol, name)