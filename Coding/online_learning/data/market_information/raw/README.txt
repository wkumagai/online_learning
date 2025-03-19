# Raw Market Data Directory

This directory contains raw, unprocessed market data files directly obtained from data sources.

## Contents

- Historical stock price data (CSV format)
- Tick data (if applicable)
- Market indices data
- Exchange rate data (if applicable)

## File Naming Convention

Files are named according to the following patterns:

1. For stock price data:
   - {SYMBOL}_{EXCHANGE}.csv (e.g., AAPL_NASDAQ.csv, 7203_T.csv)
   - Historical data files may include date ranges: {SYMBOL}_{EXCHANGE}_{START_DATE}_{END_DATE}.csv

2. For market indices:
   - {INDEX_NAME}_{EXCHANGE}.csv (e.g., NIKKEI225_T.csv, SP500_NYSE.csv)

3. For tick data:
   - {SYMBOL}_{EXCHANGE}_{DATE}_tick.csv

## Data Format

### Stock Price CSV Format
Typical columns include:
- date: Trading date (YYYY-MM-DD)
- open: Opening price
- high: Highest price during the period
- low: Lowest price during the period
- close: Closing price
- volume: Trading volume
- adj_close: Adjusted closing price (if available)

### Tick Data Format (if applicable)
- timestamp: Precise time of the trade (YYYY-MM-DD HH:MM:SS.mmm)
- price: Trade price
- volume: Trade volume
- bid: Best bid price
- ask: Best ask price
- bid_size: Bid size
- ask_size: Ask size

## Notes

- Raw data should never be modified after initial download
- Data validation and cleaning should be performed in the processing stage
- Large files may be compressed (.gz or .zip format)
- This directory may contain a large amount of data and should be backed up regularly