#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the strategy module.
"""

import os
import json
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import the module to test
from src.strategy.strategy import (
    load_existing_strategies,
    create_new_strategy,
    model_training,
    generate_signal,
    safe_rule_check,
    Strategy,
    StrategyType
)

# Test data
TEST_STRATEGY_NAME = "test_strategy"
TEST_STRATEGY_TYPE = "technical"
TEST_STRATEGY_PARAMS = {
    "window_size": 14,
    "threshold": 0.5
}

# Sample stock data
SAMPLE_STOCK_DATA = pd.DataFrame({
    'date': pd.date_range(start='2023-01-01', end='2023-01-31'),
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
        'sentiment': 0.8
    },
    {
        'title': 'New iPhone Model Announced',
        'date': '2023-01-20',
        'sentiment': 0.6
    }
]

# Sample strategy definition
SAMPLE_STRATEGY = {
    "name": TEST_STRATEGY_NAME,
    "type": TEST_STRATEGY_TYPE,
    "parameters": TEST_STRATEGY_PARAMS,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
}

@pytest.fixture
def setup_test_dirs():
    """Create temporary directories for test data."""
    os.makedirs('data/strategy/models', exist_ok=True)
    os.makedirs('data/strategy/logs', exist_ok=True)
    yield
    # Cleanup could be added here if needed

def test_load_existing_strategies():
    """Test the load_existing_strategies function."""
    # Mock the file reading
    with patch('builtins.open', MagicMock()) as mock_open:
        # Configure the mock to return sample data
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps([SAMPLE_STRATEGY])
        
        # Call the function
        strategies = load_existing_strategies()
        
        # Verify the result
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        assert strategies[0]['name'] == TEST_STRATEGY_NAME
        assert strategies[0]['type'] == TEST_STRATEGY_TYPE

def test_create_new_strategy():
    """Test the create_new_strategy function."""
    # Call the function
    strategy = create_new_strategy(
        name=TEST_STRATEGY_NAME,
        strategy_type=TEST_STRATEGY_TYPE,
        parameters=TEST_STRATEGY_PARAMS
    )
    
    # Verify the result
    assert isinstance(strategy, dict)
    assert strategy['name'] == TEST_STRATEGY_NAME
    assert strategy['type'] == TEST_STRATEGY_TYPE
    assert strategy['parameters'] == TEST_STRATEGY_PARAMS
    assert 'created_at' in strategy
    assert 'updated_at' in strategy

def test_model_training():
    """Test the model_training function."""
    # Mock the model training
    with patch('src.strategy.strategy.train_model') as mock_train:
        # Configure the mock to return a success status
        mock_train.return_value = {
            'model_path': 'data/strategy/models/test_model.pkl',
            'accuracy': 0.85,
            'training_time': 10.5
        }
        
        # Call the function
        result = model_training(
            strategy_name=TEST_STRATEGY_NAME,
            training_data=SAMPLE_STOCK_DATA,
            parameters=TEST_STRATEGY_PARAMS
        )
        
        # Verify the result
        assert isinstance(result, dict)
        assert 'model_path' in result
        assert 'accuracy' in result
        assert result['accuracy'] > 0
        
        # Verify the mock was called with expected arguments
        mock_train.assert_called_once()

def test_generate_signal():
    """Test the generate_signal function."""
    # Mock the model prediction
    with patch('src.strategy.strategy.predict_with_model') as mock_predict:
        # Configure the mock to return sample signals
        mock_predict.return_value = pd.Series([0, 1, 0, -1, 0], index=range(5))
        
        # Call the function
        signals = generate_signal(
            strategy_name=TEST_STRATEGY_NAME,
            market_data=SAMPLE_STOCK_DATA.iloc[-5:],
            news_data=SAMPLE_NEWS_DATA
        )
        
        # Verify the result
        assert isinstance(signals, pd.Series)
        assert len(signals) == 5
        assert signals.min() >= -1  # Sell signal
        assert signals.max() <= 1   # Buy signal
        
        # Verify the mock was called
        mock_predict.assert_called_once()

def test_safe_rule_check():
    """Test the safe_rule_check function."""
    # Create sample signals
    signals = pd.Series([1, 0, -1, 0, 1], index=range(5))
    
    # Create sample market data with a large price drop
    market_data = SAMPLE_STOCK_DATA.copy()
    market_data.loc[market_data.index[-1], 'close'] = market_data.loc[market_data.index[-2], 'close'] * 0.9  # 10% drop
    
    # Call the function
    safe_signals = safe_rule_check(signals, market_data)
    
    # Verify the result
    assert isinstance(safe_signals, pd.Series)
    assert len(safe_signals) == len(signals)
    
    # The last signal should be modified to 0 or -1 due to the price drop
    assert safe_signals.iloc[-1] <= 0