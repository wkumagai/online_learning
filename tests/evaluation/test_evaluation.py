#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the evaluation module.
"""

import os
import json
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import the module to test
from src.evaluation.evaluation import (
    backtest_strategy,
    realtime_evaluation,
    calculate_metrics,
    calculate_returns,
    calculate_slippage,
    EvaluationResult
)

# Test data
TEST_STRATEGY_NAME = "test_strategy"
TEST_START_DATE = "2023-01-01"
TEST_END_DATE = "2023-01-31"

# Sample stock data
SAMPLE_STOCK_DATA = pd.DataFrame({
    'date': pd.date_range(start=TEST_START_DATE, end=TEST_END_DATE),
    'open': [150.0 + i * 0.1 for i in range(31)],
    'high': [155.0 + i * 0.1 for i in range(31)],
    'low': [145.0 + i * 0.1 for i in range(31)],
    'close': [152.0 + i * 0.1 for i in range(31)],
    'volume': [1000000 + i * 10000 for i in range(31)]
})

# Sample signals
SAMPLE_SIGNALS = pd.Series([0, 1, 1, 0, -1, -1, 0, 1, 0, 0, -1, 0, 0, 1, 1, 
                           0, -1, 0, 0, 1, -1, 0, 0, 1, 1, 0, -1, -1, 0, 1, 0], 
                           index=SAMPLE_STOCK_DATA.index)

@pytest.fixture
def setup_test_dirs():
    """Create temporary directories for test data."""
    os.makedirs('data/evaluation/backtest_results', exist_ok=True)
    os.makedirs('data/evaluation/realtime_results', exist_ok=True)
    yield
    # Cleanup could be added here if needed

def test_backtest_strategy():
    """Test the backtest_strategy function."""
    # Mock the strategy loading and signal generation
    with patch('src.evaluation.evaluation.load_strategy') as mock_load:
        with patch('src.evaluation.evaluation.generate_signals') as mock_signals:
            # Configure the mocks
            mock_load.return_value = {
                'name': TEST_STRATEGY_NAME,
                'type': 'technical',
                'parameters': {'window_size': 14}
            }
            mock_signals.return_value = SAMPLE_SIGNALS
            
            # Call the function
            result = backtest_strategy(
                strategy_name=TEST_STRATEGY_NAME,
                market_data=SAMPLE_STOCK_DATA,
                start_date=TEST_START_DATE,
                end_date=TEST_END_DATE,
                initial_capital=10000.0
            )
            
            # Verify the result
            assert isinstance(result, EvaluationResult)
            assert result.strategy_name == TEST_STRATEGY_NAME
            assert result.start_date == TEST_START_DATE
            assert result.end_date == TEST_END_DATE
            assert hasattr(result, 'returns')
            assert hasattr(result, 'metrics')
            
            # Verify the mocks were called
            mock_load.assert_called_once_with(TEST_STRATEGY_NAME)
            mock_signals.assert_called_once()

def test_realtime_evaluation():
    """Test the realtime_evaluation function."""
    # Mock the strategy loading and signal generation
    with patch('src.evaluation.evaluation.load_strategy') as mock_load:
        with patch('src.evaluation.evaluation.generate_signals') as mock_signals:
            # Configure the mocks
            mock_load.return_value = {
                'name': TEST_STRATEGY_NAME,
                'type': 'technical',
                'parameters': {'window_size': 14}
            }
            mock_signals.return_value = SAMPLE_SIGNALS.iloc[-5:]
            
            # Call the function
            result = realtime_evaluation(
                strategy_name=TEST_STRATEGY_NAME,
                market_data=SAMPLE_STOCK_DATA.iloc[-5:],
                current_positions={'AAPL': 10}
            )
            
            # Verify the result
            assert isinstance(result, dict)
            assert 'signals' in result
            assert 'expected_returns' in result
            assert 'risk_metrics' in result
            
            # Verify the mocks were called
            mock_load.assert_called_once_with(TEST_STRATEGY_NAME)
            mock_signals.assert_called_once()

def test_calculate_metrics():
    """Test the calculate_metrics function."""
    # Create sample returns
    returns = pd.Series(
        [0.01, -0.005, 0.02, -0.01, 0.015, 0.005, -0.02, 0.01, 0.0, 0.005],
        index=pd.date_range(start='2023-01-01', periods=10)
    )
    
    # Call the function
    metrics = calculate_metrics(returns)
    
    # Verify the result
    assert isinstance(metrics, dict)
    assert 'total_return' in metrics
    assert 'annualized_return' in metrics
    assert 'sharpe_ratio' in metrics
    assert 'max_drawdown' in metrics
    assert 'win_rate' in metrics
    
    # Check specific metrics
    assert isinstance(metrics['total_return'], float)
    assert isinstance(metrics['sharpe_ratio'], float)
    assert 0 <= metrics['win_rate'] <= 1

def test_calculate_returns():
    """Test the calculate_returns function."""
    # Create sample data
    prices = SAMPLE_STOCK_DATA['close']
    signals = SAMPLE_SIGNALS
    
    # Call the function
    returns, positions, equity = calculate_returns(
        prices=prices,
        signals=signals,
        initial_capital=10000.0,
        commission=0.001
    )
    
    # Verify the result
    assert isinstance(returns, pd.Series)
    assert isinstance(positions, pd.Series)
    assert isinstance(equity, pd.Series)
    assert len(returns) == len(prices) - 1  # One less due to diff
    assert len(positions) == len(prices)
    assert len(equity) == len(prices)
    
    # Check that equity starts at initial capital
    assert equity.iloc[0] == 10000.0

def test_calculate_slippage():
    """Test the calculate_slippage function."""
    # Create sample data
    prices = SAMPLE_STOCK_DATA['close']
    volumes = SAMPLE_STOCK_DATA['volume']
    order_sizes = pd.Series([100, 200, 0, -150, 0], index=prices.index[:5])
    
    # Call the function
    slippage = calculate_slippage(
        prices=prices[:5],
        volumes=volumes[:5],
        order_sizes=order_sizes,
        slippage_model='fixed',
        slippage_params={'fixed_bps': 5}
    )
    
    # Verify the result
    assert isinstance(slippage, pd.Series)
    assert len(slippage) == len(order_sizes)
    
    # Check that slippage is 0 for no orders
    assert slippage[order_sizes == 0].sum() == 0
    
    # Check that slippage is positive for all orders
    assert slippage[order_sizes != 0].sum() > 0