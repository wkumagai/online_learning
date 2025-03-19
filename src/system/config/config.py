"""
Decision Making System Configuration File
"""

import os
from datetime import datetime, timedelta

# Environment Variables
US_STOCK_API_KEY = os.getenv('US_STOCK_API_KEY')
JP_STOCK_API_KEY = os.getenv('JP_STOCK_API_KEY')
LLM_API_KEY = os.getenv('LLM_API_KEY')
IB_ACCOUNT = os.getenv('IB_ACCOUNT')
IB_PORT = int(os.getenv('IB_PORT', '7497'))
IB_HOST = os.getenv('IB_HOST', '127.0.0.1')
ENV_MODE = os.getenv('ENV_MODE', 'development')

# Trading Settings
STOCK_MARKET = 'US'  # 'US' or 'JP'
PAPER_TRADING = True  # True: paper trading, False: live trading
INITIAL_CAPITAL = 1000000  # Initial capital (USD)

# Target Symbols
US_SYMBOLS = ['NVDA', 'AAPL', 'MSFT', 'GOOGL']
JP_SYMBOLS = ['7203.T', '9984.T', '6758.T', '7974.T']  # Toyota, SoftBank G, Sony, Nintendo

# Risk Management
RISK_PER_TRADE = 0.02      # Risk per trade (proportion of capital)
MAX_POSITION_SIZE = 0.1    # Maximum position size (proportion of capital)
STOP_LOSS_PCT = 0.03      # Stop loss (3%)
TAKE_PROFIT_PCT = 0.06    # Take profit (6%)

# Data Settings
DATA_INTERVAL = '1min'
START_DATE = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # From 1 year ago

# Alert Thresholds
ALERT_THRESHOLDS = {
    'drawdown': -0.03,     # Alert on 3% drawdown
    'profit': 0.05,        # Alert on 5% profit
    'volume_spike': 2.5    # Alert on 2.5x average volume
}

# Strategy Parameters
STRATEGY_PARAMS = {
    'moving_average': {
        'short_window': 10,
        'long_window': 30
    },
    'momentum': {
        'rsi_period': 14,
        'overbought': 70,
        'oversold': 30
    },
    'lstm': {
        'sequence_length': 20,
        'epochs': 50,
        'batch_size': 32
    }
}

# Feature Settings
FEATURE_COLUMNS = [
    'Close',
    'Volume',
    'RSI',
    'MACD',
    'Signal_Line',
    'BB_Upper',
    'BB_Lower',
    'Momentum'
]

# Directory Settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, 'reports')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
MODEL_SAVE_DIR = os.path.join(BASE_DIR, 'models')

# Logging Settings
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'

def create_directories():
    """Create necessary directories"""
    directories = [
        REPORT_DIR,
        LOG_DIR,
        MODEL_SAVE_DIR
    ]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

# Create directories on startup
create_directories()
