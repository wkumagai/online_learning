"""
base_executor.py

取引実行の基本インターフェースを定義するモジュール
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd
import asyncio
import logging

class BaseExecutor(ABC):
    """
    取引実行の基本インターフェース
    
    全ての実行エンジン（実運用、ペーパートレード）の基底クラス
    """
    
    def __init__(self, initial_capital: float = 1000000, risk_per_trade: float = 0.02, max_position_size: float = 0.1):
        """
        初期化
        
        Args:
            initial_capital: 初期資金
            risk_per_trade: 1トレードあたりのリスク（資金に対する割合）
            max_position_size: 最大ポジションサイズ（資金に対する割合）
        """
        self.initial_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.max_position_size = max_position_size
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def start(self) -> bool:
        """
        実行エンジンを開始
        
        Returns:
            bool: 開始に成功したかどうか
        """
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """
        実行エンジンを停止
        
        Returns:
            bool: 停止に成功したかどうか
        """
        pass
    
    @abstractmethod
    async def get_account_summary(self) -> Dict[str, Any]:
        """
        口座情報を取得
        
        Returns:
            Dict: 口座情報
        """
        pass
    
    @abstractmethod
    async def get_current_positions(self) -> Dict[str, Dict[str, Any]]:
        """
        現在のポジションを取得
        
        Returns:
            Dict: 銘柄ごとのポジション情報
        """
        pass
    
    @abstractmethod
    async def execute_signals(self, signals: Dict[str, pd.DataFrame], current_prices: Dict[str, float]) -> Dict[str, List[Dict[str, Any]]]:
        """
        取引シグナルを実行
        
        Args:
            signals: 銘柄ごとの取引シグナル
            current_prices: 銘柄ごとの現在価格
            
        Returns:
            Dict: 銘柄ごとの取引結果
        """
        pass
    
    @abstractmethod
    async def get_market_data(self, symbol: str, timeframe: str = '1d', bars: int = 100) -> Optional[pd.DataFrame]:
        """
        市場データを取得
        
        Args:
            symbol: 銘柄シンボル
            timeframe: 時間枠
            bars: バー数
            
        Returns:
            DataFrame or None: 市場データ
        """
        pass