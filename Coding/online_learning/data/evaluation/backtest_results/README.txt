# Backtest Results Directory

This directory contains the results of strategy backtests, including performance metrics, trade logs, and visualization data.

## Contents

- Backtest summary reports
- Detailed trade logs
- Performance metrics
- Equity curves
- Drawdown analysis
- Risk metrics

## File Naming Convention

Files are named according to the following patterns:

1. Backtest summary reports:
   - backtest_{STRATEGY_NAME}_{START_DATE}_{END_DATE}.json
   - Example: backtest_momentum_20200101_20221231.json

2. Detailed trade logs:
   - trades_{STRATEGY_NAME}_{START_DATE}_{END_DATE}.csv
   - Example: trades_momentum_20200101_20221231.csv

3. Equity curves:
   - equity_{STRATEGY_NAME}_{START_DATE}_{END_DATE}.csv
   - Example: equity_momentum_20200101_20221231.csv

4. Comparison reports:
   - compare_{STRATEGY_LIST}_{START_DATE}_{END_DATE}.json
   - Example: compare_momentum_mean_reversion_20200101_20221231.json

## Data Formats

### Backtest Summary JSON Format

```json
{
  "strategy_name": "momentum",
  "version": "1.2",
  "backtest_id": "bt_momentum_20230315_001",
  "parameters": {
    "window": 20,
    "threshold": 0.05
  },
  "period": {
    "start_date": "2020-01-01",
    "end_date": "2022-12-31"
  },
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "initial_capital": 100000,
  "metrics": {
    "total_return": 0.45,
    "annualized_return": 0.15,
    "sharpe_ratio": 1.2,
    "max_drawdown": 0.18,
    "win_rate": 0.62,
    "profit_factor": 1.8,
    "recovery_factor": 2.5
  },
  "trade_summary": {
    "total_trades": 124,
    "winning_trades": 77,
    "losing_trades": 47,
    "avg_profit": 450.25,
    "avg_loss": -250.75,
    "max_profit": 2500.00,
    "max_loss": -1200.00
  }
}
```

### Trade Log CSV Format

Trade logs typically include columns such as:
- date: Trade date
- symbol: Traded symbol
- action: Buy/Sell
- quantity: Number of shares/contracts
- price: Execution price
- value: Trade value
- commission: Trading commission
- slippage: Estimated slippage
- pnl: Profit/loss for the trade
- cumulative_pnl: Running total of profit/loss
- holding_period: Duration the position was held

## Notes

- Backtest results should be reproducible with the same input data and parameters
- Consider including market benchmark performance for comparison
- Slippage and commission models should be documented
- Backtest assumptions and limitations should be noted
- For large backtests, consider storing only summary data and key metrics
- Visualization scripts can generate charts from these data files