"""
paper_executor.py

ペーパートレードモードの取引実行エンジン
"""

import asyncio
import logging
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any, Optional
import os
import json
import numpy as np
import yfinance as yf

from trading.execution.base_executor import BaseExecutor

class PaperExecutor(BaseExecutor):
    """
    ペーパートレードモードの取引実行エンジン
    
    実際の取引は行わず、シミュレーションのみを行う
    """
    
    def __init__(
        self,
        initial_capital: float = 1000000,
        risk_per_trade: float = 0.02,
        max_position_size: float = 0.1,
        data_source: str = 'yahoo'
    ):
        """
        初期化
        
        Args:
            initial_capital: 初期資金
            risk_per_trade: 1トレードあたりのリスク（資金に対する割合）
            max_position_size: 最大ポジションサイズ（資金に対する割合）
            data_source: データソース（'yahoo'または'csv'）
        """
        super().__init__(initial_capital, risk_per_trade, max_position_size)
        self.data_source = data_source
        self.current_capital = initial_capital
        self.positions = {}  # 現在のポジション
        self.orders = {}     # 注文履歴
        self.trades = []     # 取引履歴
        self.running = False
        
        # パフォーマンス指標
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0,
            'equity_curve': [initial_capital]
        }
        
        # ログディレクトリの作成
        os.makedirs('logs', exist_ok=True)
    
    async def start(self) -> bool:
        """
        実行エンジンを開始
        
        Returns:
            bool: 開始に成功したかどうか
        """
        try:
            self.logger.info("ペーパートレードエンジンを開始します...")
            self.logger.info(f"初期資金: {self.initial_capital:,.0f}円")
            
            self.running = True
            return True
        except Exception as e:
            self.logger.error(f"ペーパートレードエンジンの開始に失敗しました: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """
        実行エンジンを停止
        
        Returns:
            bool: 停止に成功したかどうか
        """
        try:
            self.running = False
            
            # 最終パフォーマンスレポートの生成
            self._generate_performance_report()
            
            self.logger.info("ペーパートレードエンジンを停止しました")
            return True
        except Exception as e:
            self.logger.error(f"ペーパートレードエンジンの停止に失敗しました: {str(e)}")
            return False
    
    async def get_account_summary(self) -> Dict[str, Any]:
        """
        口座情報を取得
        
        Returns:
            Dict: 口座情報
        """
        # ポジションの時価評価額を計算
        position_value = 0.0
        for symbol, pos in self.positions.items():
            position_value += pos['position'] * pos['current_price']
        
        # 口座情報の作成
        equity = self.current_capital + position_value
        
        return {
            'NetLiquidation': {'value': equity, 'currency': 'JPY'},
            'TotalCashValue': {'value': self.current_capital, 'currency': 'JPY'},
            'GrossPositionValue': {'value': position_value, 'currency': 'JPY'},
            'AvailableFunds': {'value': self.current_capital, 'currency': 'JPY'}
        }
    
    async def get_current_positions(self) -> Dict[str, Dict[str, Any]]:
        """
        現在のポジションを取得
        
        Returns:
            Dict: 銘柄ごとのポジション情報
        """
        return self.positions
    
    async def execute_signals(
        self,
        signals: Dict[str, pd.DataFrame],
        current_prices: Dict[str, float]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        取引シグナルを実行
        
        Args:
            signals: 銘柄ごとの取引シグナル
            current_prices: 銘柄ごとの現在価格
            
        Returns:
            Dict: 銘柄ごとの取引結果
        """
        results = {}
        
        for symbol, signal_df in signals.items():
            if symbol not in current_prices:
                continue
            
            current_price = current_prices[symbol]
            latest_signal = signal_df.iloc[-1]
            
            # ポジションサイズの計算
            size = self._calculate_position_size(
                symbol,
                current_price,
                latest_signal['signal']
            )
            
            if size == 0:
                continue
            
            # 注文の実行（シミュレーション）
            try:
                action = 'BUY' if size > 0 else 'SELL'
                quantity = abs(size)
                
                # 現在のポジションを更新
                if symbol not in self.positions:
                    self.positions[symbol] = {
                        'position': 0,
                        'avg_price': 0,
                        'current_price': current_price
                    }
                
                # 取引前のポジション
                prev_position = self.positions[symbol]['position']
                
                # 取引の実行
                if action == 'BUY':
                    # 買い注文
                    cost = quantity * current_price
                    if cost > self.current_capital:
                        # 資金不足
                        self.logger.warning(f"資金不足のため注文を実行できません: {symbol} {action} {quantity} @ {current_price:,.2f}")
                        results[symbol] = [{
                            'timestamp': datetime.now(),
                            'error': '資金不足',
                            'status': 'failed'
                        }]
                        continue
                    
                    # 資金の減少
                    self.current_capital -= cost
                    
                    # ポジションの更新
                    if prev_position >= 0:
                        # 買いポジションの追加
                        total_cost = prev_position * self.positions[symbol]['avg_price'] + cost
                        total_quantity = prev_position + quantity
                        self.positions[symbol]['avg_price'] = total_cost / total_quantity if total_quantity > 0 else 0
                    else:
                        # 売りポジションのクローズ
                        if quantity > abs(prev_position):
                            # 売りポジションをクローズして買いポジションを持つ
                            close_quantity = abs(prev_position)
                            new_quantity = quantity - close_quantity
                            
                            # 決済損益の計算
                            profit = close_quantity * (self.positions[symbol]['avg_price'] - current_price)
                            self._update_performance_metrics(profit)
                            
                            # 新しい買いポジション
                            self.positions[symbol]['avg_price'] = current_price
                        else:
                            # 売りポジションの一部をクローズ
                            profit = quantity * (self.positions[symbol]['avg_price'] - current_price)
                            self._update_performance_metrics(profit)
                    
                    self.positions[symbol]['position'] += quantity
                    
                else:
                    # 売り注文
                    # ポジションの更新
                    if prev_position <= 0:
                        # 売りポジションの追加
                        total_cost = abs(prev_position) * self.positions[symbol]['avg_price'] + quantity * current_price
                        total_quantity = abs(prev_position) + quantity
                        self.positions[symbol]['avg_price'] = total_cost / total_quantity if total_quantity > 0 else 0
                    else:
                        # 買いポジションのクローズ
                        if quantity > prev_position:
                            # 買いポジションをクローズして売りポジションを持つ
                            close_quantity = prev_position
                            new_quantity = quantity - close_quantity
                            
                            # 決済損益の計算
                            profit = close_quantity * (current_price - self.positions[symbol]['avg_price'])
                            self._update_performance_metrics(profit)
                            
                            # 新しい売りポジション
                            self.positions[symbol]['avg_price'] = current_price
                        else:
                            # 買いポジションの一部をクローズ
                            profit = quantity * (current_price - self.positions[symbol]['avg_price'])
                            self._update_performance_metrics(profit)
                    
                    # 売りの場合は資金が増加
                    self.current_capital += quantity * current_price
                    
                    self.positions[symbol]['position'] -= quantity
                
                # 現在価格の更新
                self.positions[symbol]['current_price'] = current_price
                
                # 取引履歴に追加
                trade = {
                    'timestamp': datetime.now(),
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'price': current_price,
                    'value': quantity * current_price
                }
                self.trades.append(trade)
                
                # 結果の返却
                results[symbol] = [{
                    'timestamp': datetime.now(),
                    'action': action,
                    'quantity': quantity,
                    'price': current_price,
                    'status': 'executed'
                }]
                
                self.logger.info(f"注文を実行しました: {symbol} {action} {quantity} @ {current_price:,.2f}")
                
            except Exception as e:
                self.logger.error(f"{symbol}の取引実行中にエラーが発生しました: {str(e)}")
                results[symbol] = [{
                    'timestamp': datetime.now(),
                    'error': str(e),
                    'status': 'failed'
                }]
        
        # パフォーマンスデータの保存
        self._save_performance_data()
        
        return results
    
    async def get_market_data(
        self,
        symbol: str,
        timeframe: str = '1d',
        bars: int = 100
    ) -> Optional[pd.DataFrame]:
        """
        市場データを取得
        
        Args:
            symbol: 銘柄シンボル
            timeframe: 時間枠
            bars: バー数
            
        Returns:
            DataFrame or None: 市場データ
        """
        try:
            if self.data_source == 'yahoo':
                # Yahoo Financeからデータを取得
                period = '1y'
                interval = '1d'
                
                if timeframe == '1h':
                    period = '60d'
                    interval = '1h'
                elif timeframe == '1m':
                    period = '7d'
                    interval = '1m'
                
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period, interval=interval)
                
                if df.empty:
                    self.logger.warning(f"{symbol}の市場データがありません")
                    return None
                
                # カラム名の変更
                df = df.rename(columns={
                    'Open': 'Open',
                    'High': 'High',
                    'Low': 'Low',
                    'Close': 'Close',
                    'Volume': 'Volume'
                })
                
                return df
                
            else:
                # CSVファイルからデータを取得（実装例）
                csv_path = f"data/{symbol}.csv"
                if not os.path.exists(csv_path):
                    self.logger.warning(f"{symbol}のCSVファイルが見つかりません: {csv_path}")
                    return None
                
                df = pd.read_csv(csv_path)
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                
                return df
                
        except Exception as e:
            self.logger.error(f"{symbol}の市場データ取得中にエラーが発生しました: {str(e)}")
            return None
    
    def _calculate_position_size(
        self,
        symbol: str,
        current_price: float,
        signal: float
    ) -> int:
        """
        ポジションサイズを計算
        
        Args:
            symbol: 銘柄シンボル
            current_price: 現在価格
            signal: 取引シグナル
        
        Returns:
            int: 取引数量（正: 買い、負: 売り）
        """
        try:
            # リスクに基づく取引数量の計算
            risk_amount = self.current_capital * self.risk_per_trade
            max_amount = self.current_capital * self.max_position_size
            
            # 現在のポジションを考慮
            current_position = self.positions.get(symbol, {}).get('position', 0)
            
            # シグナルに基づく取引数量の決定
            if signal > 0:  # 買いシグナル
                if current_position >= 0:
                    # 新規または追加の買いポジション
                    max_additional = int(max_amount / current_price) - current_position
                    size = min(
                        int(risk_amount / current_price),
                        max_additional
                    )
                else:
                    # 売りポジションのクローズ
                    size = abs(current_position)
            elif signal < 0:  # 売りシグナル
                if current_position <= 0:
                    # 新規または追加の売りポジション
                    max_additional = int(max_amount / current_price) + current_position
                    size = -min(
                        int(risk_amount / current_price),
                        max_additional
                    )
                else:
                    # 買いポジションのクローズ
                    size = -current_position
            else:
                size = 0
            
            return size
            
        except Exception as e:
            self.logger.error(f"ポジションサイズの計算中にエラーが発生しました: {str(e)}")
            return 0
    
    def _update_performance_metrics(self, profit: float):
        """
        パフォーマンス指標を更新
        
        Args:
            profit: 取引の損益
        """
        # 取引数の更新
        self.performance_metrics['total_trades'] += 1
        
        # 損益の更新
        if profit > 0:
            self.performance_metrics['winning_trades'] += 1
            self.performance_metrics['total_profit'] += profit
        else:
            self.performance_metrics['losing_trades'] += 1
            self.performance_metrics['total_loss'] += abs(profit)
        
        # 資産の更新
        account_value = self.current_capital
        for symbol, pos in self.positions.items():
            account_value += pos['position'] * pos['current_price']
        
        self.performance_metrics['equity_curve'].append(account_value)
        
        # ドローダウンの計算
        peak = max(self.performance_metrics['equity_curve'])
        if account_value < peak:
            current_drawdown = (peak - account_value) / peak
            self.performance_metrics['current_drawdown'] = current_drawdown
            self.performance_metrics['max_drawdown'] = max(
                self.performance_metrics['max_drawdown'],
                current_drawdown
            )
    
    def _save_performance_data(self):
        """パフォーマンスデータを保存"""
        try:
            # 取引履歴の保存
            with open(f'logs/paper_trade_history_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
                json.dump([{
                    'timestamp': t['timestamp'].isoformat(),
                    'symbol': t['symbol'],
                    'action': t['action'],
                    'quantity': t['quantity'],
                    'price': t['price'],
                    'value': t['value']
                } for t in self.trades], f, indent=2)
            
            # パフォーマンス指標の保存
            metrics_copy = self.performance_metrics.copy()
            metrics_copy['equity_curve'] = metrics_copy['equity_curve'][-100:]  # 最新の100件のみ保存
            
            with open(f'logs/paper_performance_metrics_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
                json.dump(metrics_copy, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"パフォーマンスデータの保存中にエラーが発生しました: {str(e)}")
    
    def _generate_performance_report(self):
        """最終パフォーマンスレポートの生成"""
        try:
            win_rate = (self.performance_metrics['winning_trades'] / 
                       self.performance_metrics['total_trades']) if self.performance_metrics['total_trades'] > 0 else 0
            
            profit_factor = (self.performance_metrics['total_profit'] / 
                           self.performance_metrics['total_loss']) if self.performance_metrics['total_loss'] > 0 else float('inf')
            
            # 資産の計算
            account_value = self.current_capital
            for symbol, pos in self.positions.items():
                account_value += pos['position'] * pos['current_price']
            
            # リターンの計算
            total_return = (account_value - self.initial_capital) / self.initial_capital
            
            report = {
                'summary': {
                    'initial_capital': self.initial_capital,
                    'final_equity': account_value,
                    'total_return': total_return,
                    'total_trades': self.performance_metrics['total_trades'],
                    'win_rate': win_rate,
                    'profit_factor': profit_factor,
                    'max_drawdown': self.performance_metrics['max_drawdown']
                },
                'positions': self.positions,
                'trades': [{
                    'timestamp': t['timestamp'].isoformat(),
                    'symbol': t['symbol'],
                    'action': t['action'],
                    'quantity': t['quantity'],
                    'price': t['price'],
                    'value': t['value']
                } for t in self.trades],
                'metrics': self.performance_metrics
            }
            
            # レポートの保存
            with open(f'logs/paper_final_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
                json.dump(report, f, indent=2)
                
            self.logger.info("最終パフォーマンスレポートを生成しました")
            self.logger.info(f"初期資金: {self.initial_capital:,.0f}円")
            self.logger.info(f"最終資産: {account_value:,.0f}円")
            self.logger.info(f"リターン: {total_return:.2%}")
            self.logger.info(f"勝率: {win_rate:.2%}")
            self.logger.info(f"プロフィットファクター: {profit_factor:.2f}")
            self.logger.info(f"最大ドローダウン: {self.performance_metrics['max_drawdown']:.2%}")
            
        except Exception as e:
            self.logger.error(f"パフォーマンスレポートの生成中にエラーが発生しました: {str(e)}")
