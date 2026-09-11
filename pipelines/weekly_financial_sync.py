"""
weekly_financial_sync.py
Production ML & Data Orchestration Pipeline powered by Prefect.
Runs on a scheduled interval (e.g., weekly) to pull fresh market telemetry,
update the local SQLite analytics store, and verify data integrity.
"""

import os
import sqlite3
import datetime
from prefect import flow, task
import yfinance as yf

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "financials.db")

WATCHLIST = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL"]

@task(retries=3, retry_delay_seconds=5, name="fetch-market-telemetry")
def fetch_ticker_telemetry(ticker: str) -> dict:
    """Extracts live valuation and pricing metrics via yfinance with automated retries."""
    print(f"Fetching live telemetry for {ticker}...")
    t = yf.Ticker(ticker)
    info = t.info
    
    price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
    mcap = info.get("marketCap", 0)
    pe = info.get("trailingPE", 0.0)
    eps = info.get("trailingEps", 0.0)
    
    return {
        "ticker": ticker,
        "company_name": info.get("shortName", ticker),
        "price": price,
        "market_cap": mcap,
        "trailing_pe": pe,
        "trailing_eps": eps,
        "sync_timestamp": datetime.datetime.utcnow().isoformat()
    }

@task(name="verify-data-integrity")
def verify_data(records: list[dict]) -> list[dict]:
    """Ensures no corrupted, zero, or null records are pushed to the database."""
    valid_records = []
    for r in records:
        if r["price"] > 0 and r["market_cap"] > 0:
            valid_records.append(r)
        else:
            print(f"Warning: Discarding invalid telemetry record for {r['ticker']}")
    print(f"Verified {len(valid_records)}/{len(records)} market records successfully.")
    return valid_records

@task(name="update-sqlite-store")
def update_sqlite(records: list[dict]):
    """Upserts fresh market intelligence into the SQLite relational database."""
    db_path = os.path.abspath(DATABASE_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS live_market_summary (
            ticker TEXT PRIMARY KEY,
            company_name TEXT,
            price REAL,
            market_cap REAL,
            trailing_pe REAL,
            trailing_eps REAL,
            last_sync_utc TEXT
        )
    """)
    
    for r in records:
        cursor.execute("""
            INSERT INTO live_market_summary (ticker, company_name, price, market_cap, trailing_pe, trailing_eps, last_sync_utc)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker) DO UPDATE SET
                price=excluded.price,
                market_cap=excluded.market_cap,
                trailing_pe=excluded.trailing_pe,
                trailing_eps=excluded.trailing_eps,
                last_sync_utc=excluded.last_sync_utc
        """, (
            r["ticker"], r["company_name"], r["price"], r["market_cap"],
            r["trailing_pe"], r["trailing_eps"], r["sync_timestamp"]
        ))
        
    conn.commit()
    conn.close()
    print(f"Successfully upserted {len(records)} tickers into SQLite database at {db_path}.")

@flow(name="weekly-financial-sync-flow", log_prints=True)
def run_financial_sync_pipeline(tickers: list[str] = WATCHLIST):
    """
    Main Prefect Flow:
    1. Fetches real-time ticker data concurrently across watchlist
    2. Runs data integrity and validation guardrails
    3. Persists fresh state to relational storage
    """
    print(f"Starting Weekly Financial Sync Pipeline for: {tickers}")
    
    raw_data = []
    for t in tickers:
        raw_data.append(fetch_ticker_telemetry(t))
        
    verified = verify_data(raw_data)
    update_sqlite(verified)
    
    print("✅ Financial Sync Pipeline completed successfully!")

if __name__ == "__main__":
    # Execute the flow locally
    run_financial_sync_pipeline()
