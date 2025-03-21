"""
base_strategy.py

Base class for trading strategies.
All strategy classes should inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Union
import pandas as pd

class BaseStrategy(ABC):
    """Base class for trading strategies"""

    @abstractmethod
    def predict(self, 
               data: Union[pd.DataFrame, Dict[str, pd.DataFrame]], 
               symbols: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
        """
        Execute prediction
        Args:
            data: Input data (DataFrame for single symbol or dict of DataFrames for multiple symbols)
            symbols: List of target symbols (for multiple symbols)
        Returns:
            Prediction results
        """
        pass

    @abstractmethod
    def generate_signals(self, 
                        data: Union[pd.DataFrame, Dict[str, pd.DataFrame]], 
                        symbols: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
        """
        Generate trading signals
        Args:
            data: Input data
            symbols: List of target symbols
        Returns:
            Trading signals
        """
        pass

    @abstractmethod
    def validate_data(self, data: Union[pd.DataFrame, Dict[str, pd.DataFrame]]) -> bool:
        """
        Validate input data
        Args:
            data: Data to validate
        Returns:
            Validation result (True/False)
        """
        pass

    def execute(self, 
                data: Union[pd.DataFrame, Dict[str, pd.DataFrame]], 
                symbols: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
        """
        Execute strategy
        Args:
            data: Input data
            symbols: List of target symbols
        Returns:
            Trading signals
        """
        # Validate data
        if not self.validate_data(data):
            raise ValueError("Invalid input data")

        # Generate signals
        return self.generate_signals(data, symbols)

    def get_strategy_info(self) -> dict:
        """
        Get strategy information
        Returns:
            Dictionary containing strategy information
        """
        return {
            "strategy_type": self.__class__.__name__,
            "description": self.__doc__,
            "parameters": self._get_parameters()
        }

    def _get_parameters(self) -> dict:
        """
        Get strategy parameters
        Returns:
            Dictionary containing parameters
        """
        # Override in derived classes if needed
        return {}
