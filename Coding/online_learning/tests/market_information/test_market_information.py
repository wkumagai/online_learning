#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the market_information module.
"""

import os
import json
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import the module to test
from src.market_information.market_information import (
    get_stock_data,
    get_news_data,
    normalize_stock_data,
    save_data,
    StockDataSource,
    NewsDataSource
)

# Test data
TEST_SYMBOL = "AAPL"
TEST_START_DATE = "2023-01-01"
TEST_END_DATE = "2023-01-31"
TEST_INTERVAL = "1d"

# Sample stock data
SAMPLE_STOCK_DATA = pd.DataFrame({
    'date': pd.date_range(start=TEST_START_DATE, end=TEST_END_DATE),
    'open': [150.0 + i * 0.1 for i in range(31)],
    'high': [155.0 + i * 0.1 for i in range(31)],
    'low': [145.0 + i * 0.1 for i in range(31)],
    'close': [152.0 + i * 0.1 for i in range(31)],
    'volume': [1000000 + i * 10000 for i in range(31)]
})

# Sample news data
SAMPLE_NEWS_DATA = [
    {
        'title': 'Apple Reports Record Earnings',
        'date': '2023-01-15',
        'source': 'Financial Times',
        'url': 'https://example.com/news1',
        'content': 'Apple Inc. reported record earnings for the quarter...'
    },
    {
        'title': 'New iPhone Model Announced',
        'date': '2023-01-20',
        'source': 'Tech News',
        'url': 'https://example.com/news2',
        'content': 'Apple announced a new iPhone model with enhanced features...'
    }
]

@pytest.fixture
def setup_test_dirs():
    """Create temporary directories for test data."""
    os.makedirs('data/market_information/raw', exist_ok=True)
    os.makedirs('data/market_information/processed', exist_ok=True)
    os.makedirs('data/market_information/news', exist_ok=True)
    yield
    # Cleanup could be added here if needed

def test_get_stock_data():
    """Test the get_stock_data function."""
    # Mock the API call
    with patch('src.market_information.market_information.StockDataSource.fetch_from_api') as mock_fetch:
        # Configure the mock to return sample data
        mock_fetch.return_value = SAMPLE_STOCK_DATA
        
        # Call the function
        result = get_stock_data(
            symbol=TEST_SYMBOL,
            start_date=TEST_START_DATE,
            end_date=TEST_END_DATE,
            interval=TEST_INTERVAL,
            source=StockDataSource.API
        )
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'date' in result.columns
        assert 'close' in result.columns
        assert len(result) > 0
        
        # Verify the mock was called with expected arguments
        mock_fetch.assert_called_once_with(
            TEST_SYMBOL, TEST_START_DATE, TEST_END_DATE, TEST_INTERVAL
        )

def test_get_news_data():
    """Test the get_news_data function."""
    # Mock the API call
    with patch('src.market_information.market_information.NewsDataSource.fetch_from_api') as mock_fetch:
        # Configure the mock to return sample data
        mock_fetch.return_value = SAMPLE_NEWS_DATA
        
        # Call the function
        result = get_news_data(
            keywords=["Apple", "iPhone"],
            start_date=TEST_START_DATE,
            end_date=TEST_END_DATE,
            source=NewsDataSource.API
        )
        
        # Verify the result
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'title' in result[0]
        assert 'date' in result[0]
        assert 'content' in result[0]
        
        # Verify the mock was called with expected arguments
        mock_fetch.assert_called_once_with(
            ["Apple", "iPhone"], TEST_START_DATE, TEST_END_DATE
        )

def test_normalize_stock_data():
    """Test the normalize_stock_data function."""
    # Create a sample DataFrame
    df = SAMPLE_STOCK_DATA.copy()
    
    # Call the function
    result = normalize_stock_data(df)
    
    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert 'date' in result.columns
    assert 'normalized_close' in result.columns
    
    # Check normalization (values should be between 0 and 1)
    assert result['normalized_close'].min() >= 0
    assert result['normalized_close'].max() <= 1

def test_save_data(setup_test_dirs):
    """Test the save_data function."""
    # Create a sample DataFrame
    df = SAMPLE_STOCK_DATA.copy()
    
    # Define the output path
    output_path = os.path.join('data', 'market_information', 'processed', f"{TEST_SYMBOL}_{TEST_START_DATE}_{TEST_END_DATE}.csv")
    
    # Call the function
    result_path = save_data(df, output_path)
    
    # Verify the result
    assert os.path.exists(result_path)
    
    # Load the saved data and verify
    saved_df = pd.read_csv(result_path)
    assert not saved_df.empty
    assert 'date' in saved_df.columns
    assert 'close' in saved_df.columns
    assert len(saved_df) == len(df)