"""Yahoo Finance MCP data fetcher for historical market data."""
from typing import Optional
import pandas as pd
from datetime import datetime


class MCPDataFetcher:
    """Fetches historical market data via Yahoo Finance MCP server."""

    def __init__(self, mcp_client=None):
        """
        Initialize the data fetcher.

        Args:
            mcp_client: MCP client instance for Yahoo Finance server
        """
        self.mcp_client = mcp_client

    def fetch_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a symbol.

        Args:
            symbol: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval (1d, 1h, etc.)

        Returns:
            DataFrame with columns: Date, Open, High, Low, Close, Volume
        """
        if self.mcp_client is None:
            raise ValueError("MCP client not initialized")

        # Call Yahoo Finance MCP to fetch data
        # This will be integrated with the actual MCP server
        data = self.mcp_client.get_historical_data(
            symbol=symbol,
            start=start_date,
            end=end_date,
            interval=interval
        )

        return self._process_data(data)

    def _process_data(self, raw_data) -> pd.DataFrame:
        """Process raw MCP data into standard DataFrame format."""
        # Convert to DataFrame and ensure proper types
        df = pd.DataFrame(raw_data)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        # Ensure numeric columns
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col])

        return df.sort_index()
