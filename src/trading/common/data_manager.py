"""
data_manager.py

Module for fetching and managing market data.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Optional
import logging

class DataManager:
    """
    Class for fetching and managing market data.
    """

    def __init__(self, config):
        """
        Args:
            config: Module containing system-wide configuration values
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cache = {}

    def fetch_market_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch market data for a specified symbol.

        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            DataFrame containing market data
        """
        cache_key = f"{symbol}_{start_date}_{end_date}_{interval}"
        
        if cache_key in self.cache:
            self.logger.info(f"Returning cached data for {symbol}")
            return self.cache[cache_key]

        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )

            if df.empty:
                self.logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()

            # Standardize column names
            df.index.name = 'Date'
            df.columns = [col.title() for col in df.columns]

            # Save to cache
            self.cache[cache_key] = df
            
            self.logger.info(f"Successfully fetched data for {symbol}")
            return df

        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()

    def get_multiple_symbols(
        self,
        symbols: list,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> dict:
        """
        Fetch market data for multiple symbols.

        Args:
            symbols: List of stock symbols
            start_date: Start date
            end_date: End date
            interval: Data interval

        Returns:
            Dictionary with symbols as keys and DataFrames as values
        """
        data = {}
        for symbol in symbols:
            df = self.fetch_market_data(symbol, start_date, end_date, interval)
            if not df.empty:
                data[symbol] = df
        return data

    def clear_cache(self):
        """Clear the data cache"""
        self.cache.clear()
        self.logger.info("Cache cleared")
