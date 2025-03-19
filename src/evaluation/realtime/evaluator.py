"""
evaluator.py

Module for evaluating trading strategy performance.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging

class StrategyEvaluator:
    """
    Class for evaluating trading strategy performance.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            'total_return': self._calculate_total_return,
            'sharpe_ratio': self._calculate_sharpe_ratio,
            'max_drawdown': self._calculate_max_drawdown,
            'win_rate': self._calculate_win_rate,
            'profit_factor': self._calculate_profit_factor,
            'volatility': self._calculate_volatility,
            'average_trade': self._calculate_average_trade,
            'trade_count': self._calculate_trade_count
        }

    def evaluate_strategy(self, df: pd.DataFrame, initial_capital: float = 100000) -> Dict[str, float]:
        """
        Evaluate a single strategy.

        Args:
            df: DataFrame containing trading signals and results
            initial_capital: Initial capital

        Returns:
            Dictionary containing evaluation metrics
        """
        try:
            results = {}
            for metric_name, metric_func in self.metrics.items():
                results[metric_name] = metric_func(df, initial_capital)
            return results
        except Exception as e:
            self.logger.error(f"Error in strategy evaluation: {str(e)}")
            return {}

    def evaluate_multiple_strategies(
        self, 
        strategy_results: Dict[str, pd.DataFrame],
        initial_capital: float = 100000
    ) -> pd.DataFrame:
        """
        Evaluate multiple strategies and return results in a comparable format.

        Args:
            strategy_results: Dictionary with strategy names as keys and result DataFrames as values
            initial_capital: Initial capital

        Returns:
            DataFrame containing evaluation metrics for each strategy
        """
        evaluations = []
        
        for strategy_name, df in strategy_results.items():
            evaluation = self.evaluate_strategy(df, initial_capital)
            evaluation['strategy_name'] = strategy_name
            evaluations.append(evaluation)
        
        return pd.DataFrame(evaluations).set_index('strategy_name')

    def _calculate_total_return(self, df: pd.DataFrame, initial_capital: float) -> float:
        """Calculate total return"""
        final_value = df['portfolio_value'].iloc[-1]
        return (final_value - initial_capital) / initial_capital * 100

    def _calculate_sharpe_ratio(self, df: pd.DataFrame, initial_capital: float) -> float:
        """Calculate Sharpe ratio"""
        returns = df['portfolio_value'].pct_change()
        if returns.std() == 0:
            return 0
        return returns.mean() / returns.std() * np.sqrt(252)

    def _calculate_max_drawdown(self, df: pd.DataFrame, initial_capital: float) -> float:
        """Calculate maximum drawdown"""
        portfolio_values = df['portfolio_value']
        peak = portfolio_values.expanding(min_periods=1).max()
        drawdown = (portfolio_values - peak) / peak
        return drawdown.min() * 100

    def _calculate_win_rate(self, df: pd.DataFrame, initial_capital: float) -> float:
        """Calculate win rate"""
        trades = df[df['signal'] != 0]
        if len(trades) == 0:
            return 0
        returns = trades['portfolio_value'].pct_change()
        return (returns > 0).mean() * 100

    def _calculate_profit_factor(self, df: pd.DataFrame, initial_capital: float) -> float:
        """Calculate profit factor"""
        trades = df[df['signal'] != 0]
        returns = trades['portfolio_value'].pct_change()
        
        gains = returns[returns > 0].sum()
        losses = abs(returns[returns < 0].sum())
        
        if losses == 0:
            return float('inf') if gains > 0 else 0
        return gains / losses

    def _calculate_volatility(self, df: pd.DataFrame, initial_capital: float) -> float:
        """Calculate volatility"""
        returns = df['portfolio_value'].pct_change()
        return returns.std() * np.sqrt(252) * 100

    def _calculate_average_trade(self, df: pd.DataFrame, initial_capital: float) -> float:
        """Calculate average trade profit"""
        trades = df[df['signal'] != 0]
        if len(trades) == 0:
            return 0
        returns = trades['portfolio_value'].pct_change()
        return returns.mean() * 100

    def _calculate_trade_count(self, df: pd.DataFrame, initial_capital: float) -> int:
        """Calculate number of trades"""
        return len(df[df['signal'] != 0])

    def generate_detailed_report(
        self,
        strategy_results: Dict[str, pd.DataFrame],
        initial_capital: float = 100000
    ) -> Dict[str, Any]:
        """
        Generate detailed evaluation report.

        Args:
            strategy_results: Dictionary with strategy names as keys and result DataFrames as values
            initial_capital: Initial capital

        Returns:
            Dictionary containing detailed report information
        """
        report = {
            'summary': self.evaluate_multiple_strategies(strategy_results, initial_capital),
            'correlation_matrix': self._calculate_strategy_correlations(strategy_results),
            'monthly_returns': self._calculate_monthly_returns(strategy_results),
            'risk_metrics': self._calculate_risk_metrics(strategy_results, initial_capital)
        }
        return report

    def _calculate_strategy_correlations(
        self,
        strategy_results: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """Calculate return correlations between strategies"""
        returns_dict = {}
        for name, df in strategy_results.items():
            returns_dict[name] = df['portfolio_value'].pct_change()
        
        returns_df = pd.DataFrame(returns_dict)
        return returns_df.corr()

    def _calculate_monthly_returns(
        self,
        strategy_results: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """Calculate monthly returns"""
        monthly_returns = {}
        for name, df in strategy_results.items():
            monthly = df['portfolio_value'].resample('M').last().pct_change()
            monthly_returns[name] = monthly
        
        return pd.DataFrame(monthly_returns)

    def _calculate_risk_metrics(
        self,
        strategy_results: Dict[str, pd.DataFrame],
        initial_capital: float
    ) -> pd.DataFrame:
        """Calculate risk metrics"""
        risk_metrics = {}
        for name, df in strategy_results.items():
            returns = df['portfolio_value'].pct_change()
            risk_metrics[name] = {
                'var_95': returns.quantile(0.05),
                'cvar_95': returns[returns <= returns.quantile(0.05)].mean(),
                'worst_drawdown': self._calculate_max_drawdown(df, initial_capital),
                'volatility': returns.std() * np.sqrt(252)
            }
        
        return pd.DataFrame(risk_metrics).T
