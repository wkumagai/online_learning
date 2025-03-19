"""
simple_ma.py

単純移動平均戦略
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

from trading.common.strategy_manager import Strategy

class SimpleMAStrategy(Strategy):
    """
    単純移動平均戦略
    
    短期移動平均が長期移動平均を上回ったら買い
    短期移動平均が長期移動平均を下回ったら売り
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初期化
        
        Args:
            params: 戦略パラメータ
                - short_window: 短期移動平均の期間 (デフォルト: 20)
                - long_window: 長期移動平均の期間 (デフォルト: 50)
        """
        default_params = {
            'short_window': 20,
            'long_window': 50
        }
        
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
        
        self.short_window = self.params['short_window']
        self.long_window = self.params['long_window']
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        テクニカル指標を計算
        
        Args:
            data: 市場データ
            
        Returns:
            DataFrame: テクニカル指標を追加したデータ
        """
        # データのコピーを作成
        df = data.copy()
        
        # 短期移動平均の計算
        df['short_ma'] = df['Close'].rolling(window=self.short_window).mean()
        
        # 長期移動平均の計算
        df['long_ma'] = df['Close'].rolling(window=self.long_window).mean()
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        取引シグナルを生成
        
        Args:
            data: 市場データ
            
        Returns:
            DataFrame: 取引シグナル
        """
        # テクニカル指標の計算
        df = self.calculate_indicators(data)
        
        # シグナル列の初期化
        df['signal'] = 0.0
        
        # クロスオーバーの検出
        df['signal'] = np.where(df['short_ma'] > df['long_ma'], 1.0, 0.0)
        
        # シグナルの変化点を検出
        df['position'] = df['signal'].diff()
        
        # 結果のDataFrameを作成
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['Close']
        signals['short_ma'] = df['short_ma']
        signals['long_ma'] = df['long_ma']
        signals['signal'] = df['signal']
        signals['position'] = df['position']
        
        return signals

class TripleMAStrategy(Strategy):
    """
    三重移動平均戦略
    
    短期、中期、長期の3つの移動平均を使用
    短期>中期>長期の場合は強い買いシグナル
    短期<中期<長期の場合は強い売りシグナル
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初期化
        
        Args:
            params: 戦略パラメータ
                - short_window: 短期移動平均の期間 (デフォルト: 10)
                - mid_window: 中期移動平均の期間 (デフォルト: 30)
                - long_window: 長期移動平均の期間 (デフォルト: 50)
        """
        default_params = {
            'short_window': 10,
            'mid_window': 30,
            'long_window': 50
        }
        
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
        
        self.short_window = self.params['short_window']
        self.mid_window = self.params['mid_window']
        self.long_window = self.params['long_window']
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        テクニカル指標を計算
        
        Args:
            data: 市場データ
            
        Returns:
            DataFrame: テクニカル指標を追加したデータ
        """
        # データのコピーを作成
        df = data.copy()
        
        # 短期移動平均の計算
        df['short_ma'] = df['Close'].rolling(window=self.short_window).mean()
        
        # 中期移動平均の計算
        df['mid_ma'] = df['Close'].rolling(window=self.mid_window).mean()
        
        # 長期移動平均の計算
        df['long_ma'] = df['Close'].rolling(window=self.long_window).mean()
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        取引シグナルを生成
        
        Args:
            data: 市場データ
            
        Returns:
            DataFrame: 取引シグナル
        """
        # テクニカル指標の計算
        df = self.calculate_indicators(data)
        
        # シグナル列の初期化
        df['signal'] = 0.0
        
        # 強い買いシグナル: 短期 > 中期 > 長期
        strong_buy = (df['short_ma'] > df['mid_ma']) & (df['mid_ma'] > df['long_ma'])
        
        # 強い売りシグナル: 短期 < 中期 < 長期
        strong_sell = (df['short_ma'] < df['mid_ma']) & (df['mid_ma'] < df['long_ma'])
        
        # 弱い買いシグナル: 短期 > 長期
        weak_buy = (df['short_ma'] > df['long_ma']) & ~strong_buy
        
        # 弱い売りシグナル: 短期 < 長期
        weak_sell = (df['short_ma'] < df['long_ma']) & ~strong_sell
        
        # シグナルの設定
        df['signal'] = np.where(strong_buy, 1.0, 
                      np.where(strong_sell, -1.0, 
                      np.where(weak_buy, 0.5, 
                      np.where(weak_sell, -0.5, 0.0))))
        
        # シグナルの変化点を検出
        df['position'] = df['signal'].diff()
        
        # 結果のDataFrameを作成
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['Close']
        signals['short_ma'] = df['short_ma']
        signals['mid_ma'] = df['mid_ma']
        signals['long_ma'] = df['long_ma']
        signals['signal'] = df['signal']
        signals['position'] = df['position']
        
        return signals