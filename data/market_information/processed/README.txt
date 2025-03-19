# Processed Market Data Directory

This directory contains processed and transformed market data that has been cleaned, normalized, or otherwise prepared for analysis and model training.

## Contents

- Cleaned stock price data
- Feature-engineered datasets
- Normalized price data
- Technical indicators
- Merged datasets

## File Naming Convention

Files are named according to the following patterns:

1. Cleaned data:
   - cleaned_{SYMBOL}_{EXCHANGE}.csv

2. Feature-engineered data:
   - features_{SYMBOL}_{EXCHANGE}_{FEATURE_SET}.csv
   - Example: features_AAPL_NASDAQ_technical.csv

3. Normalized data:
   - normalized_{SYMBOL}_{EXCHANGE}.csv

4. Technical indicators:
   - indicators_{SYMBOL}_{EXCHANGE}.csv

5. Merged datasets:
   - merged_{DATASET_TYPE}_{DATE_RANGE}.csv
   - Example: merged_tech_stocks_20230101_20230630.csv

## Data Format

Processed data files typically include:
- Original price data columns (date, open, high, low, close, volume)
- Additional calculated columns (e.g., moving averages, RSI, MACD)
- Normalized values (e.g., normalized_close, z_score)
- Feature columns for model training

## Processing Operations

Common processing operations include:
- Handling missing values
- Removing outliers
- Calculating technical indicators
- Normalizing price data
- Feature engineering
- Merging multiple data sources

## Notes

- All processing operations should be reproducible and documented
- Processing scripts are located in src/market_infomation/
- Processed data should include metadata about the processing steps applied
- Large files may be stored in compressed format (.gz or .zip)