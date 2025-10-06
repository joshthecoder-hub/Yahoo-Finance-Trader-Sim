"""
Tests for Yahoo Finance data fetcher.
"""
import pytest
import pandas as pd
from datetime import datetime
from src.data.fetchTickerData import fetch_ticker_data


class TestDataFetcher:
    """Test suite for Yahoo Finance data fetcher."""

    def test_fetch_valid_ticker(self):
        """Test fetching data for a valid ticker symbol."""
        data = fetch_ticker_data(
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-01-31",
            interval="1d"
        )

        # Verify data structure
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert data.index.name == 'Date'

        # Verify columns
        expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        assert list(data.columns) == expected_columns

        # Verify data types
        for col in ['Open', 'High', 'Low', 'Close']:
            assert data[col].dtype in ['float64', 'float32']
        assert data['Volume'].dtype in ['int64', 'float64']

        # Verify date index
        assert isinstance(data.index, pd.DatetimeIndex)
        assert data.index.tz is None  # Should be timezone-naive

    def test_fetch_invalid_ticker(self):
        """Test that invalid ticker raises ValueError."""
        with pytest.raises(ValueError, match="Error fetching data"):
            fetch_ticker_data(
                symbol="INVALID_TICKER_XYZ123",
                start_date="2024-01-01",
                end_date="2024-01-31"
            )

    def test_date_range(self):
        """Test that fetched data respects date range."""
        start = "2024-01-01"
        end = "2024-01-31"

        data = fetch_ticker_data(
            symbol="AAPL",
            start_date=start,
            end_date=end
        )

        # First date should be on or after start_date
        assert data.index[0] >= pd.Timestamp(start)
        # Last date should be before end_date
        assert data.index[-1] < pd.Timestamp(end)

    def test_ohlc_relationships(self):
        """Test that OHLC data has valid relationships."""
        data = fetch_ticker_data(
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )

        # High should be >= Low
        assert (data['High'] >= data['Low']).all()

        # High should be >= Open and Close
        assert (data['High'] >= data['Open']).all()
        assert (data['High'] >= data['Close']).all()

        # Low should be <= Open and Close
        assert (data['Low'] <= data['Open']).all()
        assert (data['Low'] <= data['Close']).all()

    def test_no_missing_values(self):
        """Test that fetched data has no missing OHLCV values."""
        data = fetch_ticker_data(
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )

        # Should have no NaN values in OHLCV columns
        assert not data[['Open', 'High', 'Low', 'Close', 'Volume']].isna().any().any()

    def test_positive_prices(self):
        """Test that all prices are positive."""
        data = fetch_ticker_data(
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )

        # All price columns should be positive
        assert (data['Open'] > 0).all()
        assert (data['High'] > 0).all()
        assert (data['Low'] > 0).all()
        assert (data['Close'] > 0).all()
        assert (data['Volume'] >= 0).all()

    def test_sorted_index(self):
        """Test that data is sorted by date in ascending order."""
        data = fetch_ticker_data(
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )

        # Index should be sorted
        assert data.index.is_monotonic_increasing


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
