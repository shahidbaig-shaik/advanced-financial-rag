import os
import re
from typing import Optional, Any
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

COMMON_TICKERS = {
    "apple": "AAPL",
    "aapl": "AAPL",
    "tesla": "TSLA",
    "tsla": "TSLA",
    "nvidia": "NVDA",
    "nvda": "NVDA",
    "microsoft": "MSFT",
    "msft": "MSFT",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "googl": "GOOGL",
    "amazon": "AMZN",
    "amzn": "AMZN",
    "meta": "META",
    "facebook": "META"
}

def extract_ticker(question: str) -> str:
    """Extracts ticker symbol using keyword lookup with fallback to regex or default."""
    q_lower = question.lower()
    for name, sym in COMMON_TICKERS.items():
        if name in q_lower:
            return sym
            
    # Check for $TICKER pattern
    match = re.search(r"\$([A-Za-z]{1,5})\b", question)
    if match:
        return match.group(1).upper()
        
    return "AAPL"

def query_live_market_data(question: str, langfuse_handler: Optional[Any] = None) -> str:
    """Fetches real-time market data from Yahoo Finance and formats a live market report."""
    ticker_symbol = extract_ticker(question)
    print(f"  [Live Market Tool]: Fetching live market metrics for '{ticker_symbol}' via yfinance...")
    
    try:
        t = yf.Ticker(ticker_symbol)
        info = t.info
        
        company_name = info.get("shortName") or info.get("longName") or ticker_symbol
        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
        prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose") or price
        change = price - prev_close if prev_close else 0.0
        change_pct = (change / prev_close) * 100 if prev_close else 0.0
        
        market_cap = info.get("marketCap", 0)
        if market_cap >= 1e12:
            mcap_str = f"${market_cap / 1e12:.2f} Trillion"
        elif market_cap >= 1e9:
            mcap_str = f"${market_cap / 1e9:.2f} Billion"
        else:
            mcap_str = f"${market_cap:,.2f}"
            
        day_low = info.get("dayLow", "N/A")
        day_high = info.get("dayHigh", "N/A")
        low_52w = info.get("fiftyTwoWeekLow", "N/A")
        high_52w = info.get("fiftyTwoWeekHigh", "N/A")
        
        pe_trailing = round(info["trailingPE"], 2) if info.get("trailingPE") else "N/A"
        pe_forward = round(info["forwardPE"], 2) if info.get("forwardPE") else "N/A"
        eps_trailing = round(info["trailingEps"], 2) if info.get("trailingEps") else "N/A"
        recommendation = info.get("recommendationKey", "N/A").capitalize()
        target_price = f"${info.get('targetMeanPrice', 'N/A')}" if info.get("targetMeanPrice") else "N/A"
        currency = info.get("currency", "USD")

        sign = "+" if change >= 0 else ""
        direction = "📈" if change >= 0 else "📉"
        
        report = f"""### {direction} Real-Time Market Intelligence: {company_name} (`{ticker_symbol}`)

**Current Market Quote:**
- **Live Stock Price:** **${price:.2f} {currency}** ({sign}{change:.2f} / {sign}{change_pct:.2f}%)
- **Today's Trading Range:** ${day_low} — ${day_high}
- **52-Week Range:** ${low_52w} — ${high_52w}

**Valuation & Financial Metrics:**
- **Market Capitalization:** **{mcap_str}**
- **Trailing P/E Ratio:** {pe_trailing}
- **Forward P/E Ratio:** {pe_forward}
- **Diluted EPS (TTM):** ${eps_trailing}
- **Wall Street Consensus:** **{recommendation}** (12-Mo Target: {target_price})

*Data source: Real-time telemetry via Yahoo Finance API (`yfinance`).*
"""
        return report

    except Exception as e:
        print(f"Error in Live Market Tool: {e}")
        return f"Unable to fetch real-time market data for `{ticker_symbol}`: {str(e)}"
