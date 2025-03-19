# Model Training

Machine Learning Model Training System for Stock Price Prediction (MVP Version)

## Overview

- Stock price data retrieval using Alpha Vantage API
- Price prediction model training using LSTM
- 1-minute interval predictions (using latest 100 data points)

## Requirements

- Python 3.8 or higher
- Alpha Vantage API Key

## Installation

```bash
# Install required packages
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file to configure API keys and other settings
```

## Configuration

The following settings can be configured in the .env file:

```env
# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY=your_api_key_here

# Data Settings
TARGET_SYMBOL=NVDA
DATA_INTERVAL=1min
START_DATE=2024-12-01

# Model Settings
MODEL_TYPE=lstm
SEQUENCE_LENGTH=10
PREDICTION_TARGET=1
```

## Usage

### Basic Execution

```bash
# Run with default settings
python main.py

# Run with specific parameters
python main.py --symbol NVDA --interval 1min
```

### Data Structure

```
model_training/
├── data/
│   ├── raw/        # Raw data
│   ├── processed/  # Processed data
│   └── features/   # Feature data
├── models/         # Trained models
└── logs/          # Log files
```

## Implemented Features

1. Data Collection
- Stock price data retrieval using Alpha Vantage API
- 1-minute interval data retrieval (latest 100 entries)
- Data caching functionality

2. Feature Generation
- Technical indicator calculations
- Sequence data generation
- Data scaling

3. Model Training
- LSTM model construction
- Training/validation/test data splitting
- Model saving functionality

## Limitations (MVP Version)

1. Data Retrieval
- Alpha Vantage free plan limitations (5 requests per minute)
- 1-minute interval data limited to latest 100 entries

2. Model
- Simple LSTM model only
- Limited training data

3. Evaluation
- Basic evaluation metrics only
- No real-time validation

## Future Development

1. Data Collection Expansion
- Longer-term data collection
- Multiple timeframe support
- Additional data sources

2. Model Improvements
- Multiple model architectures
- Hyperparameter optimization
- Ensemble learning

3. Evaluation Enhancement
- More detailed performance analysis
- Backtesting functionality
- Real-time validation implementation

## Important Notes

- This system is an MVP (Minimum Viable Product) version
- Thorough validation is required for actual trading
- Be mindful of API limitations

## Google Colab Usage

1. File Structure
```
time-series/
└── model_training/
    └── notebooks/
        └── ModelTraining.ipynb  # Google Colab notebook
```

2. Execution Steps
- Upload the `time-series` folder to Google Drive
- Open `ModelTraining.ipynb` in Google Colab
- Follow the notebook instructions

3. Important Notes
- Initial setup includes package installation and configuration
- Initial setup cells can be skipped after first run
- For GPU usage, select it under "Runtime" → "Change runtime type"
- Trained models are saved in the `model_training/models` directory

4. Troubleshooting
- If execution errors occur, try "Runtime" → "Restart runtime"
- If package installation fails, try installing packages individually using `!pip install`
