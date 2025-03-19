"""
rsi.py

RSI（相対力指数）戦略
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

from trading.common.strategy_manager import Strategy

class RSIStrategy(Strategy):
    """
    RSI（相対力指数）戦略
    
    RSIが下限値を下回ったら買い
    RSIが上限値を上回ったら売り
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初期化
        
        Args:
            params: 戦略パラメータ
                - period: RSIの計算期間 (デフォルト: 14)
                - upper_bound: 売りシグナルの閾値 (デフォルト: 70)
                - lower_bound: 買いシグナルの閾値 (デフォルト: 30)
        """
        default_params = {
            'period': 14,
            'upper_bound': 70,
            'lower_bound': 30
        }
        
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
        
        self.period = self.params['period']
        self.upper_bound = self.params['upper_bound']
        self.lower_bound = self.params['lower_bound']
    
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
        
        # 価格変化の計算
        df['price_change'] = df['Close'].diff()
        
        # 上昇幅と下落幅の計算
        df['gain'] = np.where(df['price_change'] > 0, df['price_change'], 0)
        df['loss'] = np.where(df['price_change'] < 0, -df['price_change'], 0)
        
        # 平均上昇幅と平均下落幅の計算
        df['avg_gain'] = df['gain'].rolling(window=self.period).mean()
        df['avg_loss'] = df['loss'].rolling(window=self.period).mean()
        
        # RSの計算
        df['rs'] = df['avg_gain'] / df['avg_loss']
        
        # RSIの計算
        df['rsi'] = 100 - (100 / (1 + df['rs']))
        
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
        
        # 買いシグナル: RSIが下限値を下回る
        df['signal'] = np.where(df['rsi'] < self.lower_bound, 1.0, df['signal'])
        
        # 売りシグナル: RSIが上限値を上回る
        df['signal'] = np.where(df['rsi'] > self.upper_bound, -1.0, df['signal'])
        
        # シグナルの変化点を検出
        df['position'] = df['signal'].diff()
        
        # 結果のDataFrameを作成
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['Close']
        signals['rsi'] = df['rsi']
        signals['signal'] = df['signal']
        signals['position'] = df['position']
        
        return signals

class RSIWithTrendStrategy(Strategy):
    """
    トレンド確認付きRSI戦略
    
    RSIに加えて移動平均でトレンドを確認
    上昇トレンドでRSIが下限値を下回ったら買い
    下降トレンドでRSIが上限値を上回ったら売り
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初期化
        
        Args:
            params: 戦略パラメータ
                - rsi_period: RSIの計算期間 (デフォルト: 14)
                - upper_bound: 売りシグナルの閾値 (デフォルト: 70)
                - lower_bound: 買いシグナルの閾値 (デフォルト: 30)
                - ma_period: トレンド確認用移動平均の期間 (デフォルト: 50)
        """
        default_params = {
            'rsi_period': 14,
            'upper_bound': 70,
            'lower_bound': 30,
            'ma_period': 50
        }
        
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
        
        self.rsi_period = self.params['rsi_period']
        self.upper_bound = self.params['upper_bound']
        self.lower_bound = self.params['lower_bound']
        self.ma_period = self.params['ma_period']
    
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
        
        # 移動平均の計算
        df['ma'] = df['Close'].rolling(window=self.ma_period).mean()
        
        # トレンドの判定
        df['trend'] = np.where(df['Close'] > df['ma'], 1, -1)
        
        # 価格変化の計算
        df['price_change'] = df['Close'].diff()
        
        # 上昇幅と下落幅の計算
        df['gain'] = np.where(df['price_change'] > 0, df['price_change'], 0)
        df['loss'] = np.where(df['price_change'] < 0, -df['price_change'], 0)
        
        # 平均上昇幅と平均下落幅の計算
        df['avg_gain'] = df['gain'].rolling(window=self.rsi_period).mean()
        df['avg_loss'] = df['loss'].rolling(window=self.rsi_period).mean()
        
        # RSの計算
        df['rs'] = df['avg_gain'] / df['avg_loss']
        
        # RSIの計算
        df['rsi'] = 100 - (100 / (1 + df['rs']))
        
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
        
        # 買いシグナル: 上昇トレンドでRSIが下限値を下回る
        buy_condition = (df['trend'] == 1) & (df['rsi'] < self.lower_bound)
        df['signal'] = np.where(buy_condition, 1.0, df['signal'])
        
        # 売りシグナル: 下降トレンドでRSIが上限値を上回る
        sell_condition = (df['trend'] == -1) & (df['rsi'] > self.upper_bound)
        df['signal'] = np.where(sell_condition, -1.0, df['signal'])
        
        # シグナルの変化点を検出
        df['position'] = df['signal'].diff()
        
        # 結果のDataFrameを作成
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['Close']
        signals['ma'] = df['ma']
        signals['trend'] = df['trend']
        signals['rsi'] = df['rsi']
        signals['signal'] = df['signal']
        signals['position'] = df['position']
        
        return signals