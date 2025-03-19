# Strategy Models Directory

This directory contains trained machine learning models and other algorithmic trading strategy components used for market prediction and signal generation.

## Contents

- Machine learning models (saved in various formats)
- Model metadata and performance metrics
- Model version history
- Strategy configuration files
- Model checkpoints

## Directory Structure

The models directory is organized by strategy type:

```
models/
├── ML/                  # Machine learning based strategies
│   ├── regression/      # Price prediction models
│   ├── classification/  # Direction prediction models
│   └── deep_learning/   # Neural network models
├── Technical/           # Technical indicator based strategies
├── Fundamental/         # Fundamental analysis strategies
├── Sentiment/           # News and sentiment based strategies
└── Ensemble/            # Combined strategy models
```

## File Naming Convention

Files are named according to the following patterns:

1. Machine learning models:
   - {MODEL_TYPE}_{SYMBOL_OR_MARKET}_{FEATURES}_{VERSION}.{EXT}
   - Example: lstm_AAPL_price_seq_v1.2.h5

2. Strategy configurations:
   - {STRATEGY_NAME}_config_{VERSION}.json
   - Example: momentum_reversal_config_v2.1.json

3. Model metadata:
   - {MODEL_FILENAME}.meta.json
   - Example: lstm_AAPL_price_seq_v1.2.meta.json

## Model Metadata Format

Each model should have an accompanying metadata file in JSON format with information such as:

```json
{
  "model_name": "lstm_AAPL_price_seq",
  "version": "1.2",
  "created_at": "2023-03-15T14:30:00Z",
  "author": "trading_system",
  "framework": "tensorflow",
  "input_features": ["close_norm_5d", "volume_norm_5d", "rsi_14", "macd"],
  "output_features": ["price_direction_1d"],
  "training_period": {
    "start_date": "2020-01-01",
    "end_date": "2022-12-31"
  },
  "validation_metrics": {
    "accuracy": 0.68,
    "precision": 0.71,
    "recall": 0.65,
    "f1_score": 0.68
  },
  "hyperparameters": {
    "layers": 2,
    "units": 64,
    "dropout": 0.2,
    "learning_rate": 0.001
  },
  "description": "LSTM model for predicting next-day price direction of AAPL"
}
```

## Notes

- Models should be versioned to track changes and improvements
- Large model files may be stored with Git LFS or in a separate model registry
- Model training code is located in src/strategy/training/
- Models should be regularly evaluated and retrained as needed
- Consider implementing model monitoring to detect performance degradation