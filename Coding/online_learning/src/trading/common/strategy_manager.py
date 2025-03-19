"""
strategy_manager.py

取引戦略の管理を行うモジュール
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Callable, Type
import importlib
import inspect
import os
import sys

class Strategy:
    """
    取引戦略の基底クラス
    
    全ての戦略はこのクラスを継承する必要がある
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初期化
        
        Args:
            params: 戦略パラメータ
        """
        self.params = params or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        取引シグナルを生成
        
        Args:
            data: 市場データ
            
        Returns:
            DataFrame: 取引シグナル
        """
        raise NotImplementedError("サブクラスで実装する必要があります")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        テクニカル指標を計算
        
        Args:
            data: 市場データ
            
        Returns:
            DataFrame: テクニカル指標を追加したデータ
        """
        return data

class StrategyManager:
    """
    取引戦略の管理クラス
    
    複数の戦略を管理し、実行する
    """
    
    def __init__(self):
        """初期化"""
        self.logger = logging.getLogger(__name__)
        self.strategies = {}  # 戦略の辞書
        self.active_strategies = {}  # 銘柄ごとのアクティブな戦略
    
    def register_strategy(self, name: str, strategy: Strategy) -> bool:
        """
        戦略を登録
        
        Args:
            name: 戦略名
            strategy: 戦略インスタンス
            
        Returns:
            bool: 登録に成功したかどうか
        """
        try:
            self.strategies[name] = strategy
            self.logger.info(f"戦略を登録しました: {name}")
            return True
        except Exception as e:
            self.logger.error(f"戦略の登録に失敗しました: {str(e)}")
            return False
    
    def load_strategies(self, directory: str = 'strategies') -> int:
        """
        ディレクトリから戦略を読み込む
        
        Args:
            directory: 戦略が格納されているディレクトリ
            
        Returns:
            int: 読み込んだ戦略の数
        """
        count = 0
        try:
            # ディレクトリのパスを追加
            sys.path.append(os.path.abspath(directory))
            
            # ディレクトリ内のPythonファイルを検索
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        # モジュールパスの作成
                        rel_path = os.path.relpath(os.path.join(root, file), directory)
                        module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
                        
                        try:
                            # モジュールの読み込み
                            module = importlib.import_module(module_path)
                            
                            # Strategyを継承したクラスを検索
                            for name, obj in inspect.getmembers(module):
                                if (inspect.isclass(obj) and 
                                    issubclass(obj, Strategy) and 
                                    obj != Strategy):
                                    # 戦略インスタンスの作成と登録
                                    strategy = obj()
                                    self.register_strategy(name, strategy)
                                    count += 1
                        except Exception as e:
                            self.logger.error(f"モジュールの読み込みに失敗しました: {module_path} - {str(e)}")
            
            self.logger.info(f"{count}個の戦略を読み込みました")
            return count
        except Exception as e:
            self.logger.error(f"戦略の読み込みに失敗しました: {str(e)}")
            return 0
    
    def set_active_strategy(self, symbol: str, strategy_name: str) -> bool:
        """
        銘柄に対してアクティブな戦略を設定
        
        Args:
            symbol: 銘柄シンボル
            strategy_name: 戦略名
            
        Returns:
            bool: 設定に成功したかどうか
        """
        if strategy_name not in self.strategies:
            self.logger.error(f"戦略が見つかりません: {strategy_name}")
            return False
        
        self.active_strategies[symbol] = strategy_name
        self.logger.info(f"{symbol}に対して{strategy_name}を設定しました")
        return True
    
    def execute(self, symbol: str, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        戦略を実行
        
        Args:
            symbol: 銘柄シンボル
            data: 市場データ
            
        Returns:
            Dict: 銘柄ごとの取引シグナル
        """
        try:
            # アクティブな戦略の取得
            strategy_name = self.active_strategies.get(symbol)
            if not strategy_name:
                # デフォルト戦略の使用
                if len(self.strategies) > 0:
                    strategy_name = list(self.strategies.keys())[0]
                    self.logger.warning(f"{symbol}にデフォルト戦略を使用します: {strategy_name}")
                else:
                    self.logger.error(f"{symbol}に使用可能な戦略がありません")
                    return {}
            
            strategy = self.strategies[strategy_name]
            
            # 戦略の実行
            signals = strategy.generate_signals(data)
            
            return {symbol: signals}
            
        except Exception as e:
            self.logger.error(f"{symbol}の戦略実行中にエラーが発生しました: {str(e)}")
            return {}
    
    def execute_all(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        全ての銘柄に対して戦略を実行
        
        Args:
            data: 銘柄ごとの市場データ
            
        Returns:
            Dict: 銘柄ごとの取引シグナル
        """
        results = {}
        
        for symbol, symbol_data in data.items():
            signals = self.execute(symbol, symbol_data)
            results.update(signals)
        
        return results
    
    def get_available_strategies(self) -> List[str]:
        """
        利用可能な戦略の一覧を取得
        
        Returns:
            List: 戦略名のリスト
        """
        return list(self.strategies.keys())
    
    def get_strategy_info(self, strategy_name: str) -> Dict[str, Any]:
        """
        戦略の情報を取得
        
        Args:
            strategy_name: 戦略名
            
        Returns:
            Dict: 戦略情報
        """
        if strategy_name not in self.strategies:
            return {}
        
        strategy = self.strategies[strategy_name]
        
        return {
            'name': strategy_name,
            'class': strategy.__class__.__name__,
            'module': strategy.__class__.__module__,
            'params': strategy.params
        }
