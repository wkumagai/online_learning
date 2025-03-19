#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the trading module.
"""

import os
import json
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import the module to test
from src.trading.trading import (
    Order,
    OrderType,
    OrderSide,
    OrderStatus,
    DummyBroker,
    APIBroker,
    place_order,
    handle_order_result,
    save_order_log,
    load_order_logs
)

# Test data
TEST_SYMBOL = "AAPL"
TEST_QUANTITY = 10
TEST_PRICE = 150.0

@pytest.fixture
def sample_order():
    """Create a sample order for testing."""
    return Order(
        symbol=TEST_SYMBOL,
        side=OrderSide.BUY,
        quantity=TEST_QUANTITY,
        order_type=OrderType.LIMIT,
        price=TEST_PRICE
    )

@pytest.fixture
def setup_test_dirs():
    """Create temporary directories for test data."""
    os.makedirs('data/trading/order_logs', exist_ok=True)
    yield
    # Cleanup could be added here if needed

def test_order_creation(sample_order):
    """Test the Order class creation."""
    # Verify the order properties
    assert sample_order.symbol == TEST_SYMBOL
    assert sample_order.side == OrderSide.BUY
    assert sample_order.quantity == TEST_QUANTITY
    assert sample_order.order_type == OrderType.LIMIT
    assert sample_order.price == TEST_PRICE
    assert sample_order.status == OrderStatus.PENDING
    assert sample_order.filled_quantity == 0
    assert sample_order.order_id is not None

def test_order_to_dict(sample_order):
    """Test the Order.to_dict method."""
    # Convert order to dictionary
    order_dict = sample_order.to_dict()
    
    # Verify the dictionary
    assert isinstance(order_dict, dict)
    assert order_dict['symbol'] == TEST_SYMBOL
    assert order_dict['side'] == OrderSide.BUY
    assert order_dict['quantity'] == TEST_QUANTITY
    assert order_dict['order_type'] == OrderType.LIMIT
    assert order_dict['price'] == TEST_PRICE
    assert order_dict['status'] == OrderStatus.PENDING

def test_dummy_broker_place_order(sample_order):
    """Test the DummyBroker.place_order method."""
    # Create a broker with 100% fill probability
    broker = DummyBroker(fill_probability=1.0, delay_seconds=0.1)
    
    # Place the order
    result = broker.place_order(sample_order)
    
    # Verify the result
    assert result.status == OrderStatus.FILLED
    assert result.filled_quantity == TEST_QUANTITY
    assert result.filled_price is not None
    assert result.commission > 0

def test_dummy_broker_cancel_order():
    """Test the DummyBroker.cancel_order method."""
    # Create a broker
    broker = DummyBroker()
    
    # Create and place an order
    order = Order(
        symbol=TEST_SYMBOL,
        side=OrderSide.BUY,
        quantity=TEST_QUANTITY,
        order_type=OrderType.LIMIT,
        price=TEST_PRICE
    )
    placed_order = broker.place_order(order)
    
    # Try to cancel the order
    if placed_order.status == OrderStatus.PENDING:
        # Should succeed for pending orders
        result = broker.cancel_order(placed_order.order_id)
        assert result is True
    else:
        # Should fail for filled orders
        result = broker.cancel_order(placed_order.order_id)
        assert result is False

def test_api_broker_place_order(sample_order):
    """Test the APIBroker.place_order method."""
    # Mock the requests.Session
    with patch('requests.Session') as mock_session:
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'orderId': '12345',
            'status': 'filled',
            'filledQuantity': TEST_QUANTITY,
            'filledPrice': TEST_PRICE
        }
        mock_session.return_value.post.return_value = mock_response
        
        # Create a broker
        broker = APIBroker(
            api_key='test_key',
            api_secret='test_secret',
            base_url='https://api.example.com'
        )
        
        # Place the order
        result = broker.place_order(sample_order)
        
        # Verify the result
        assert result.status == OrderStatus.FILLED
        assert result.order_id == '12345'
        
        # Verify the mock was called
        mock_session.return_value.post.assert_called_once()

def test_place_order_function(sample_order):
    """Test the place_order function."""
    # Mock the broker
    mock_broker = MagicMock()
    mock_broker.place_order.return_value = sample_order
    
    # Mock the save_order_log and handle_order_result functions
    with patch('src.trading.trading.save_order_log') as mock_save:
        with patch('src.trading.trading.handle_order_result') as mock_handle:
            # Call the function
            result = place_order(mock_broker, sample_order)
            
            # Verify the result
            assert result == sample_order
            
            # Verify the mocks were called
            mock_broker.place_order.assert_called_once_with(sample_order)
            mock_save.assert_called_once_with(sample_order)
            mock_handle.assert_called_once_with(sample_order)

def test_handle_order_result(sample_order):
    """Test the handle_order_result function."""
    # Set the order status
    sample_order.status = OrderStatus.FILLED
    sample_order.filled_quantity = TEST_QUANTITY
    sample_order.filled_price = TEST_PRICE
    
    # Call the function (should not raise any exceptions)
    handle_order_result(sample_order)
    
    # Test with different statuses
    for status in [OrderStatus.PARTIALLY_FILLED, OrderStatus.REJECTED, 
                  OrderStatus.CANCELLED, OrderStatus.EXPIRED, OrderStatus.PENDING]:
        sample_order.status = status
        handle_order_result(sample_order)

def test_save_and_load_order_logs(sample_order, setup_test_dirs):
    """Test the save_order_log and load_order_logs functions."""
    # Set the order status
    sample_order.status = OrderStatus.FILLED
    sample_order.filled_quantity = TEST_QUANTITY
    sample_order.filled_price = TEST_PRICE
    
    # Save the order log
    save_order_log(sample_order)
    
    # Load the order logs for today
    today = datetime.now().strftime('%Y-%m-%d')
    logs = load_order_logs(today)
    
    # Verify the logs
    assert isinstance(logs, list)
    assert len(logs) > 0
    
    # Find the saved order
    saved_order = None
    for log in logs:
        if log.get('order_id') == sample_order.order_id:
            saved_order = log
            break
    
    # Verify the saved order
    assert saved_order is not None
    assert saved_order['symbol'] == TEST_SYMBOL
    assert saved_order['quantity'] == TEST_QUANTITY
    assert saved_order['price'] == TEST_PRICE