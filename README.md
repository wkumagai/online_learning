# Online Learning Trading System

## Overview

This project implements an online learning trading system that continuously adapts to market conditions. The system integrates market data collection, strategy development, backtesting, real-time evaluation, and trading execution within a unified framework.

## Key Features

- **Market Data Collection**: Fetches and processes stock price data and financial news
- **Strategy Development**: Supports technical, fundamental, and machine learning-based strategies
- **Backtesting**: Evaluates strategies against historical data with realistic trading conditions
- **Real-time Evaluation**: Monitors strategy performance in live market conditions
- **Trading Execution**: Executes trades through broker APIs or paper trading
- **Reporting & Alerts**: Generates performance reports and sends alerts for significant events
- **System Management**: Handles configuration, logging, and system health monitoring

## Project Structure

```
online_learning/
├── data/                      # Data storage
│   ├── market_information/    # Market data (raw, processed, news)
│   ├── strategy/              # Strategy models and logs
│   ├── evaluation/            # Backtest and real-time evaluation results
│   ├── trading/               # Order logs and execution records
│   └── report/                # Generated reports and alerts
├── src/                       # Source code
│   ├── market_information/    # Market data collection and processing
│   ├── strategy/              # Strategy development and management
│   ├── evaluation/            # Backtesting and evaluation
│   ├── trading/               # Order execution and management
│   ├── report/                # Reporting and alerting
│   └── system/                # System configuration and management
├── tests/                     # Unit and integration tests
├── docs/                      # Documentation
├── .env                       # Environment variables (create from .env.example)
├── .gitignore                 # Git ignore file
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/online_learning.git
   cd online_learning
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. Create necessary directories:
   ```bash
   python -m src.system.setup
   ```

## Usage

### Market Data Collection

```bash
# Fetch stock data for specific symbols
python -m src.market_information.market_information --symbols AAPL,MSFT,GOOGL --start-date 2023-01-01

# Fetch news data
python -m src.market_information.market_information --news --keywords "technology,earnings" --start-date 2023-01-01
```

### Strategy Development and Backtesting

```bash
# Create a new strategy
python -m src.strategy.strategy --create --name momentum_strategy --type technical

# Run backtest
python -m src.evaluation.evaluation --backtest --strategy momentum_strategy --start-date 2023-01-01 --end-date 2023-06-30
```

### Trading Execution

```bash
# Paper trading
python -m src.trading.trading --mode paper --strategy momentum_strategy

# Live trading (use with caution)
python -m src.trading.trading --mode live --strategy momentum_strategy
```

### Reporting

```bash
# Generate performance report
python -m src.report.report --type performance --strategy momentum_strategy --format html

# Set up alerts
python -m src.report.report --configure-alerts --level warning --channel email
```

## Testing

Run the test suite:

```bash
pytest
```

Run specific tests:

```bash
pytest tests/market_information/
pytest tests/strategy/test_strategy.py
```

## Documentation

Detailed documentation is available in the `docs/` directory:

- [Market Information](docs/market_information.md)
- [Strategy Development](docs/strategy.md)
- [Evaluation](docs/evaluation.md)
- [Trading](docs/trading.md)
- [Reporting](docs/report.md)
- [System Management](docs/system.md)
