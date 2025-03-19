# Realtime Evaluation Results Directory

This directory contains the results of real-time strategy evaluations, including performance metrics, signal accuracy, and comparison with backtest expectations.

## Contents

- Real-time performance logs
- Signal accuracy reports
- Expectation vs. reality comparisons
- Daily/weekly/monthly performance summaries
- Strategy drift detection reports

## File Naming Convention

Files are named according to the following patterns:

1. Real-time performance logs:
   - realtime_{STRATEGY_NAME}_{DATE}.json
   - Example: realtime_momentum_20230315.json

2. Signal accuracy reports:
   - signals_accuracy_{STRATEGY_NAME}_{PERIOD}.csv
   - Example: signals_accuracy_momentum_daily_20230315.csv

3. Expectation vs. reality comparisons:
   - backtest_vs_real_{STRATEGY_NAME}_{PERIOD}.json
   - Example: backtest_vs_real_momentum_monthly_202303.json

4. Performance summaries:
   - performance_{STRATEGY_NAME}_{PERIOD_TYPE}_{PERIOD}.json
   - Example: performance_momentum_weekly_20230315.json

## Data Formats

### Real-time Performance JSON Format

```json
{
  "strategy_name": "momentum",
  "version": "1.2",
  "date": "2023-03-15",
  "symbols_evaluated": ["AAPL", "MSFT", "GOOGL"],
  "signals_generated": 5,
  "signals_accuracy": 0.80,
  "daily_pnl": 1250.50,
  "cumulative_pnl": 15750.25,
  "metrics": {
    "sharpe_ratio_daily": 1.8,
    "volatility_daily": 0.012,
    "max_drawdown_current": 0.05
  },
  "strategy_drift": {
    "detected": false,
    "drift_score": 0.12,
    "threshold": 0.30
  }
}
```

### Signal Accuracy CSV Format

Signal accuracy reports typically include columns such as:
- timestamp: Signal generation time
- symbol: Target symbol
- signal_type: Buy/Sell/Hold
- signal_strength: Confidence level (0-1)
- actual_direction: Actual price movement
- correct: Whether the signal was correct (true/false)
- expected_return: Expected return from signal
- actual_return: Actual return achieved
- time_horizon: Signal time horizon (e.g., 1d, 5d)

## Real-time vs. Backtest Comparison

The system regularly compares real-time performance with backtest expectations to detect:
- Strategy drift
- Market regime changes
- Implementation differences
- Data quality issues

## Notes

- Real-time evaluation results are critical for monitoring strategy health
- Performance metrics should be calculated consistently with backtest metrics
- Consider implementing alerts for significant deviations from expected performance
- Real-time results should be reviewed regularly to detect issues early
- Historical real-time results provide valuable data for strategy improvement