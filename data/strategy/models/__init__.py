"""
Trading Strategies Package

This package provides various trading strategies including:
- Technical Analysis based strategies
- Machine Learning based strategies
- Base classes for strategy development
"""

from .base import BaseStrategy
from .moving_average import MovingAverageStrategy
from .deep_learning import DeepLearningStrategy

__version__ = "0.1.0"
