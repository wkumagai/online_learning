# Order Logs Directory

This directory contains logs of all trading orders, including order details, execution status, and trade outcomes.

## Contents

- Order submission logs
- Order execution logs
- Order cancellation logs
- Trade settlement records
- Position updates

## File Naming Convention

Files are named according to the following patterns:

1. Daily order logs:
   - orders_{DATE}.json
   - Example: orders_20230315.json

2. Order execution logs:
   - executions_{DATE}.json
   - Example: executions_20230315.json

3. Position updates:
   - positions_{DATE}.json
   - Example: positions_20230315.json

## Data Formats

### Order Log JSON Format

```json
[
  {
    "order_id": "ord_20230315_001",
    "timestamp": "2023-03-15T09:30:00.123Z",
    "symbol": "AAPL",
    "side": "buy",
    "order_type": "limit",
    "quantity": 100,
    "price": 150.25,
    "time_in_force": "day",
    "status": "submitted",
    "strategy_id": "momentum_v1.2",
    "account_id": "trading_account_001",
    "tags": ["momentum", "technical"]
  },
  {
    "order_id": "ord_20230315_002",
    "timestamp": "2023-03-15T09:31:15.456Z",
    "symbol": "MSFT",
    "side": "sell",
    "order_type": "market",
    "quantity": 50,
    "time_in_force": "day",
    "status": "submitted",
    "strategy_id": "momentum_v1.2",
    "account_id": "trading_account_001",
    "tags": ["momentum", "technical"]
  }
]
```

### Execution Log JSON Format

```json
[
  {
    "execution_id": "exec_20230315_001",
    "order_id": "ord_20230315_001",
    "timestamp": "2023-03-15T09:30:05.789Z",
    "symbol": "AAPL",
    "side": "buy",
    "quantity": 100,
    "price": 150.25,
    "value": 15025.00,
    "commission": 7.50,
    "exchange": "NASDAQ",
    "status": "filled"
  },
  {
    "execution_id": "exec_20230315_002",
    "order_id": "ord_20230315_002",
    "timestamp": "2023-03-15T09:31:20.123Z",
    "symbol": "MSFT",
    "side": "sell",
    "quantity": 50,
    "price": 245.75,
    "value": 12287.50,
    "commission": 6.15,
    "exchange": "NASDAQ",
    "status": "filled"
  }
]
```

### Position Log JSON Format

```json
{
  "timestamp": "2023-03-15T16:00:00.000Z",
  "account_id": "trading_account_001",
  "cash_balance": 52500.75,
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": 100,
      "avg_price": 150.25,
      "current_price": 152.50,
      "market_value": 15250.00,
      "unrealized_pnl": 225.00,
      "unrealized_pnl_pct": 0.015
    },
    {
      "symbol": "GOOGL",
      "quantity": 25,
      "avg_price": 2200.50,
      "current_price": 2250.25,
      "market_value": 56256.25,
      "unrealized_pnl": 1243.75,
      "unrealized_pnl_pct": 0.0226
    }
  ],
  "total_value": 124007.00,
  "daily_pnl": 1468.75
}
```

## Order Status Workflow

Orders typically follow this status workflow:
1. submitted: Order has been submitted to the broker
2. accepted: Order has been accepted by the broker
3. pending: Order is pending execution
4. partially_filled: Order has been partially executed
5. filled: Order has been completely executed
6. cancelled: Order has been cancelled
7. rejected: Order has been rejected
8. expired: Order has expired without execution

## Notes

- Order logs are critical for compliance and audit purposes
- All order interactions should be logged, even failed submissions
- Order IDs should be unique and traceable
- Consider implementing a backup system for order logs
- Order logs should be retained according to regulatory requirements
- Sensitive account information should be properly secured