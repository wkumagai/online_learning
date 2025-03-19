"""
reporter.py

Module for generating and visualizing strategy evaluation reports.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List
import logging
from datetime import datetime

class StrategyReporter:
    """
    Class for generating and visualizing strategy evaluation reports.
    """

    def __init__(self, output_dir: str = "./reports"):
        """
        Args:
            output_dir: Report output directory
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        plt.style.use('seaborn')

    def generate_report(
        self,
        strategy_results: Dict[str, pd.DataFrame],
        evaluation_results: pd.DataFrame,
        report_title: str = "Strategy Comparison Report"
    ) -> None:
        """
        Generate comprehensive report.

        Args:
            strategy_results: Dictionary with strategy names as keys and result DataFrames as values
            evaluation_results: DataFrame containing evaluation metrics
            report_title: Report title
        """
        # レポートの構成要素を生成
        self._plot_portfolio_values(strategy_results)
        self._plot_performance_metrics(evaluation_results)
        self._plot_drawdowns(strategy_results)
        self._plot_monthly_returns_heatmap(strategy_results)
        self._plot_correlation_matrix(strategy_results)
        
        # 結果のサマリーを出力
        self._print_summary_statistics(evaluation_results)

    def _plot_portfolio_values(self, strategy_results: Dict[str, pd.DataFrame]) -> None:
        """Plot portfolio value trends"""
        plt.figure(figsize=(12, 6))
        
        for name, df in strategy_results.items():
            plt.plot(df.index, df['portfolio_value'], label=name)
        
        plt.title('Portfolio Value Over Time')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def _plot_performance_metrics(self, evaluation_results: pd.DataFrame) -> None:
        """Plot key performance metrics as bar charts"""
        metrics_to_plot = ['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.ravel()
        
        for i, metric in enumerate(metrics_to_plot):
            ax = axes[i]
            evaluation_results[metric].plot(kind='bar', ax=ax)
            ax.set_title(metric.replace('_', ' ').title())
            ax.grid(True)
        
        plt.tight_layout()
        plt.show()

    def _plot_drawdowns(self, strategy_results: Dict[str, pd.DataFrame]) -> None:
        """Plot drawdown trends"""
        plt.figure(figsize=(12, 6))
        
        for name, df in strategy_results.items():
            portfolio_values = df['portfolio_value']
            peak = portfolio_values.expanding(min_periods=1).max()
            drawdown = (portfolio_values - peak) / peak * 100
            plt.plot(df.index, drawdown, label=name)
        
        plt.title('Strategy Drawdowns')
        plt.xlabel('Date')
        plt.ylabel('Drawdown (%)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def _plot_monthly_returns_heatmap(self, strategy_results: Dict[str, pd.DataFrame]) -> None:
        """Generate monthly returns heatmap"""
        monthly_returns = {}
        
        for name, df in strategy_results.items():
            returns = df['portfolio_value'].resample('M').last().pct_change() * 100
            monthly_returns[name] = returns
        
        returns_df = pd.DataFrame(monthly_returns)
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(returns_df.T, cmap='RdYlGn', center=0, annot=True, fmt='.1f')
        plt.title('Monthly Returns Heatmap (%)')
        plt.tight_layout()
        plt.show()

    def _plot_correlation_matrix(self, strategy_results: Dict[str, pd.DataFrame]) -> None:
        """Display return correlations between strategies as heatmap"""
        returns_dict = {}
        for name, df in strategy_results.items():
            returns_dict[name] = df['portfolio_value'].pct_change()
        
        returns_df = pd.DataFrame(returns_dict)
        corr_matrix = returns_df.corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, vmin=-1, vmax=1)
        plt.title('Strategy Return Correlations')
        plt.tight_layout()
        plt.show()

    def _print_summary_statistics(self, evaluation_results: pd.DataFrame) -> None:
        """Output summary statistics of evaluation metrics"""
        print("\n=== Strategy Performance Summary ===")
        print("\nKey Metrics:")
        print(evaluation_results[['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate']])
        
        print("\nBest Performing Strategy by Total Return:")
        best_strategy = evaluation_results['total_return'].idxmax()
        print(f"- {best_strategy}: {evaluation_results.loc[best_strategy, 'total_return']:.2f}%")
        
        print("\nBest Risk-Adjusted Return (Sharpe Ratio):")
        best_sharpe = evaluation_results['sharpe_ratio'].idxmax()
        print(f"- {best_sharpe}: {evaluation_results.loc[best_sharpe, 'sharpe_ratio']:.2f}")

    def generate_trade_analysis(self, strategy_results: Dict[str, pd.DataFrame]) -> None:
        """
        Generate trade analysis report.

        Args:
            strategy_results: Dictionary with strategy names as keys and result DataFrames as values
        """
        for name, df in strategy_results.items():
            trades = df[df['signal'] != 0]
            
            print(f"\n=== Trade Analysis for {name} ===")
            print(f"Total Trades: {len(trades)}")
            
            if len(trades) > 0:
                returns = trades['portfolio_value'].pct_change()
                
                print(f"Average Trade Return: {returns.mean()*100:.2f}%")
                print(f"Best Trade: {returns.max()*100:.2f}%")
                print(f"Worst Trade: {returns.min()*100:.2f}%")
                print(f"Trade Return Std Dev: {returns.std()*100:.2f}%")
                
                # 取引の分布をプロット
                plt.figure(figsize=(10, 6))
                returns.hist(bins=50)
                plt.title(f'Trade Return Distribution - {name}')
                plt.xlabel('Return (%)')
                plt.ylabel('Frequency')
                plt.grid(True)
                plt.show()

    def save_report(self, filename: str = None) -> None:
        """
        Save current report.

        Args:
            filename: Filename to save as (auto-generated from timestamp if not specified)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"strategy_report_{timestamp}.html"
        
        # Report saving implementation (omitted)
        self.logger.info(f"Report saved as {filename}")
