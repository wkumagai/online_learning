#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Trading module for executing orders (dummy or real API).
This module handles order placement, result handling, and order logging.
"""

import os
import json
import time
import logging
import datetime
import requests
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('data', 'trading', 'order_logs', 'trading.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Order types and status enums
class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class Order:
    """Class representing an order."""
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "day"
    order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0
    filled_price: Optional[float] = None
    commission: float = 0
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now().isoformat()
        if self.order_id is None:
            self.order_id = f"{self.symbol}_{int(time.time())}_{id(self)}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary."""
        return asdict(self)

class BaseBroker:
    """Base broker class for order execution."""
    
    def place_order(self, order: Order) -> Order:
        """Place an order with the broker."""
        raise NotImplementedError("Subclasses must implement place_order")
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order by order_id."""
        raise NotImplementedError("Subclasses must implement cancel_order")
    
    def get_order_status(self, order_id: str) -> Optional[Order]:
        """Get the status of an order by order_id."""
        raise NotImplementedError("Subclasses must implement get_order_status")

class DummyBroker(BaseBroker):
    """Dummy broker for simulated trading."""
    
    def __init__(self, fill_probability: float = 0.95, delay_seconds: float = 0.5):
        """
        Initialize the dummy broker.
        
        Args:
            fill_probability: Probability of order being filled (0.0-1.0)
            delay_seconds: Simulated delay in seconds for order processing
        """
        self.fill_probability = fill_probability
        self.delay_seconds = delay_seconds
        self.orders: Dict[str, Order] = {}
        logger.info("Initialized DummyBroker with fill_probability=%.2f, delay=%.2fs", 
                   fill_probability, delay_seconds)
    
    def place_order(self, order: Order) -> Order:
        """Simulate placing an order."""
        logger.info(f"Placing order: {order.to_dict()}")
        
        # Simulate processing delay
        time.sleep(self.delay_seconds)
        
        # Store the order
        self.orders[order.order_id] = order
        
        # Simulate order fill (simple random model)
        import random
        if random.random() < self.fill_probability:
            # Simulate a successful fill
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            
            # Simulate execution price with small slippage
            if order.price is not None:
                slippage = order.price * random.uniform(-0.001, 0.001)
                order.filled_price = order.price + slippage
            else:
                # For market orders, simulate a price
                base_price = 100.0  # Dummy base price
                order.filled_price = base_price * random.uniform(0.99, 1.01)
            
            # Simulate commission
            order.commission = order.filled_quantity * order.filled_price * 0.001
            
            logger.info(f"Order filled: {order.to_dict()}")
        else:
            # Simulate rejection
            order.status = OrderStatus.REJECTED
            logger.warning(f"Order rejected: {order.to_dict()}")
        
        return order
    
    def cancel_order(self, order_id: str) -> bool:
        """Simulate cancelling an order."""
        if order_id not in self.orders:
            logger.warning(f"Order {order_id} not found for cancellation")
            return False
        
        order = self.orders[order_id]
        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
            logger.warning(f"Cannot cancel order {order_id} with status {order.status}")
            return False
        
        order.status = OrderStatus.CANCELLED
        logger.info(f"Order {order_id} cancelled")
        return True
    
    def get_order_status(self, order_id: str) -> Optional[Order]:
        """Get the status of an order."""
        if order_id not in self.orders:
            logger.warning(f"Order {order_id} not found")
            return None
        
        return self.orders[order_id]

class APIBroker(BaseBroker):
    """Broker that uses a real trading API."""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str):
        """
        Initialize the API broker.
        
        Args:
            api_key: API key for authentication
            api_secret: API secret for authentication
            base_url: Base URL for API endpoints
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        })
        logger.info(f"Initialized APIBroker with base_url={base_url}")
    
    def place_order(self, order: Order) -> Order:
        """Place an order using the API."""
        logger.info(f"Placing order via API: {order.to_dict()}")
        
        try:
            # Prepare the order payload
            payload = {
                'symbol': order.symbol,
                'side': order.side.value,
                'quantity': order.quantity,
                'type': order.order_type.value,
                'timeInForce': order.time_in_force
            }
            
            # Add optional parameters if present
            if order.price is not None:
                payload['price'] = order.price
            if order.stop_price is not None:
                payload['stopPrice'] = order.stop_price
            
            # Send the request to the API
            response = self.session.post(
                f"{self.base_url}/orders",
                json=payload
            )
            
            # Handle the response
            if response.status_code == 200:
                # Update the order with the response data
                response_data = response.json()
                order.order_id = response_data.get('orderId', order.order_id)
                order.status = OrderStatus(response_data.get('status', OrderStatus.PENDING.value))
                logger.info(f"Order placed successfully: {order.order_id}")
            else:
                # Handle error
                order.status = OrderStatus.REJECTED
                logger.error(f"API error: {response.status_code} - {response.text}")
            
            return order
        
        except Exception as e:
            # Handle exceptions
            order.status = OrderStatus.REJECTED
            logger.exception(f"Exception placing order: {str(e)}")
            return order
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order using the API."""
        logger.info(f"Cancelling order via API: {order_id}")
        
        try:
            response = self.session.delete(f"{self.base_url}/orders/{order_id}")
            
            if response.status_code == 200:
                logger.info(f"Order {order_id} cancelled successfully")
                return True
            else:
                logger.error(f"API error cancelling order: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.exception(f"Exception cancelling order: {str(e)}")
            return False
    
    def get_order_status(self, order_id: str) -> Optional[Order]:
        """Get the status of an order using the API."""
        logger.info(f"Getting status for order: {order_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/orders/{order_id}")
            
            if response.status_code == 200:
                # Convert API response to Order object
                data = response.json()
                
                order = Order(
                    symbol=data.get('symbol'),
                    side=OrderSide(data.get('side')),
                    quantity=float(data.get('quantity')),
                    order_type=OrderType(data.get('type')),
                    price=float(data.get('price')) if 'price' in data else None,
                    stop_price=float(data.get('stopPrice')) if 'stopPrice' in data else None,
                    time_in_force=data.get('timeInForce', 'day'),
                    order_id=data.get('orderId'),
                    status=OrderStatus(data.get('status')),
                    filled_quantity=float(data.get('filledQuantity', 0)),
                    filled_price=float(data.get('filledPrice')) if 'filledPrice' in data else None,
                    commission=float(data.get('commission', 0)),
                    timestamp=data.get('timestamp')
                )
                
                return order
            else:
                logger.error(f"API error getting order status: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            logger.exception(f"Exception getting order status: {str(e)}")
            return None

def place_order(broker: BaseBroker, order: Order) -> Order:
    """
    Place an order using the specified broker.
    
    Args:
        broker: The broker to use for placing the order
        order: The order to place
    
    Returns:
        The updated order with status and fill information
    """
    logger.info(f"Placing order for {order.symbol}: {order.side.value} {order.quantity} @ {order.price}")
    
    # Maximum number of retries
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Attempt to place the order
            result = broker.place_order(order)
            
            # Save the order log
            save_order_log(result)
            
            # Handle the order result
            handle_order_result(result)
            
            return result
        
        except Exception as e:
            retry_count += 1
            logger.error(f"Error placing order (attempt {retry_count}/{max_retries}): {str(e)}")
            
            if retry_count < max_retries:
                # Wait before retrying (exponential backoff)
                wait_time = 2 ** retry_count
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                # Max retries reached, update order status and log
                order.status = OrderStatus.REJECTED
                save_order_log(order)
                logger.error(f"Failed to place order after {max_retries} attempts")
                return order

def handle_order_result(order: Order) -> None:
    """
    Handle the result of an order placement.
    
    Args:
        order: The order with updated status
    """
    if order.status == OrderStatus.FILLED:
        logger.info(f"Order {order.order_id} filled: {order.filled_quantity} @ {order.filled_price}")
        # Here you could update portfolio, notify other components, etc.
    
    elif order.status == OrderStatus.PARTIALLY_FILLED:
        logger.info(f"Order {order.order_id} partially filled: {order.filled_quantity}/{order.quantity} @ {order.filled_price}")
        # Handle partial fills
    
    elif order.status == OrderStatus.REJECTED:
        logger.warning(f"Order {order.order_id} rejected")
        # Handle rejection (e.g., notify user, adjust strategy)
    
    elif order.status == OrderStatus.CANCELLED:
        logger.info(f"Order {order.order_id} cancelled")
        # Handle cancellation
    
    elif order.status == OrderStatus.EXPIRED:
        logger.info(f"Order {order.order_id} expired")
        # Handle expiration
    
    else:  # PENDING
        logger.info(f"Order {order.order_id} is pending")
        # Could set up monitoring for pending orders

def save_order_log(order: Order) -> None:
    """
    Save an order to the order log file.
    
    Args:
        order: The order to save
    """
    # Ensure the log directory exists
    log_dir = os.path.join('data', 'trading', 'order_logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a log file for the current day
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f"orders_{today}.json")
    
    # Convert order to dictionary
    order_dict = order.to_dict()
    
    # Convert enum values to strings for JSON serialization
    for key, value in order_dict.items():
        if isinstance(value, Enum):
            order_dict[key] = value.value
    
    # Load existing logs if the file exists
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error reading log file {log_file}, starting new log")
    
    # Add the new order log
    logs.append(order_dict)
    
    # Write the updated logs back to the file
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    logger.info(f"Order {order.order_id} logged to {log_file}")

def load_order_logs(date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load order logs for a specific date or today if not specified.
    
    Args:
        date: Date string in 'YYYY-MM-DD' format, or None for today
    
    Returns:
        List of order dictionaries
    """
    if date is None:
        date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    log_file = os.path.join('data', 'trading', 'order_logs', f"orders_{date}.json")
    
    if not os.path.exists(log_file):
        logger.warning(f"No order logs found for {date}")
        return []
    
    try:
        with open(log_file, 'r') as f:
            logs = json.load(f)
        logger.info(f"Loaded {len(logs)} order logs for {date}")
        return logs
    
    except Exception as e:
        logger.error(f"Error loading order logs for {date}: {str(e)}")
        return []

# Example usage
if __name__ == "__main__":
    # Create a dummy broker
    broker = DummyBroker(fill_probability=0.9, delay_seconds=0.2)
    
    # Create a sample order
    order = Order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=10,
        order_type=OrderType.LIMIT,
        price=150.0
    )
    
    # Place the order
    result = place_order(broker, order)
    
    # Print the result
    print(f"Order result: {result.to_dict()}")
    
    # Load today's order logs
    logs = load_order_logs()
    print(f"Today's orders: {len(logs)}")