"""Yahoo Finance data fetcher using yfinance library."""
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Optional


def fetch_ticker_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "1d"
) -> pd.DataFrame:
    """
    Fetch historical OHLCV data from Yahoo Finance.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval - valid values: 1d, 1wk, 1mo

    Returns:
        DataFrame with columns: Date (index), Open, High, Low, Close, Volume

    Raises:
        ValueError: If the ticker symbol is invalid or no data is returned
    """
    try:
        # Download data from Yahoo Finance
        ticker = yf.Ticker(symbol)
        data = ticker.history(
            start=start_date,
            end=end_date,
            interval=interval
        )

        if data.empty:
            raise ValueError(f"No data returned for {symbol} between {start_date} and {end_date}")

        # Rename columns to match expected format (remove spaces, standardize)
        data = data.rename(columns={
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Close': 'Close',
            'Volume': 'Volume'
        })

        # Keep only OHLCV columns
        data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

        # Ensure the index is named 'Date'
        data.index.name = 'Date'

        # Remove timezone info if present
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)

        print(f"✓ Fetched {len(data)} days of data for {symbol}")
        print(f"  Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")

        return data

    except Exception as e:
        raise ValueError(f"Error fetching data for {symbol}: {str(e)}")


if __name__ == "__main__":
    # Example usage
    print("Testing Yahoo Finance data fetcher...")
    print("-" * 60)

    # Fetch Apple data
    try:
        data = fetch_ticker_data(
            symbol="AAPL",
            start_date="2023-01-01",
            end_date="2023-12-31",
            interval="1d"
        )

        print("\nFirst 5 rows:")
        print(data.head())

        print("\nLast 5 rows:")
        print(data.tail())

        print("\nData info:")
        print(f"  Shape: {data.shape}")
        print(f"  Columns: {list(data.columns)}")
        print(f"  Index: {data.index.name}")

    except Exception as e:
        print(f"Error: {e}")
