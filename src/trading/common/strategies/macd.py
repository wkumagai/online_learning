"""
macd.py

MACD（移動平均収束拡散）戦略
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

from trading.common.strategy_manager import Strategy

class MACDStrategy(Strategy):
    """
    MACD（移動平均収束拡散）戦略
    
    MACDがシグナルラインを上抜けたら買い
    MACDがシグナルラインを下抜けたら売り
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初期化
        
        Args:
            params: 戦略パラメータ
                - fast_period: 短期EMAの期間 (デフォルト: 12)
                - slow_period: 長期EMAの期間 (デフォルト: 26)
                - signal_period: シグナルラインの期間 (デフォルト: 9)
        """
        default_params = {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }
        
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
        
        self.fast_period = self.params['fast_period']
        self.slow_period = self.params['slow_period']
        self.signal_period = self.params['signal_period']
    
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
        
        # 短期EMAの計算
        df['ema_fast'] = df['Close'].ewm(span=self.fast_period, adjust=False).mean()
        
        # 長期EMAの計算
        df['ema_slow'] = df['Close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # MACDラインの計算
        df['macd'] = df['ema_fast'] - df['ema_slow']
        
        # シグナルラインの計算
        df['signal_line'] = df['macd'].ewm(span=self.signal_period, adjust=False).mean()
        
        # ヒストグラムの計算
        df['histogram'] = df['macd'] - df['signal_line']
        
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
        
        # 買いシグナル: MACDがシグナルラインを上抜け
        df['signal'] = np.where(df['macd'] > df['signal_line'], 1.0, 0.0)
        
        # シグナルの変化点を検出
        df['position'] = df['signal'].diff()
        
        # 結果のDataFrameを作成
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['Close']
        signals['macd'] = df['macd']
        signals['signal_line'] = df['signal_line']
        signals['histogram'] = df['histogram']
        signals['signal'] = df['signal']
        signals['position'] = df['position']
        
        return signals

class MACDHistogramStrategy(Strategy):
    """
    MACDヒストグラム戦略
    
    ヒストグラムが正から負に変化したら売り
    ヒストグラムが負から正に変化したら買い
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初期化
        
        Args:
            params: 戦略パラメータ
                - fast_period: 短期EMAの期間 (デフォルト: 12)
                - slow_period: 長期EMAの期間 (デフォルト: 26)
                - signal_period: シグナルラインの期間 (デフォルト: 9)
        """
        default_params = {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }
        
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
        
        self.fast_period = self.params['fast_period']
        self.slow_period = self.params['slow_period']
        self.signal_period = self.params['signal_period']
    
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
        
        # 短期EMAの計算
        df['ema_fast'] = df['Close'].ewm(span=self.fast_period, adjust=False).mean()
        
        # 長期EMAの計算
        df['ema_slow'] = df['Close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # MACDラインの計算
        df['macd'] = df['ema_fast'] - df['ema_slow']
        
        # シグナルラインの計算
        df['signal_line'] = df['macd'].ewm(span=self.signal_period, adjust=False).mean()
        
        # ヒストグラムの計算
        df['histogram'] = df['macd'] - df['signal_line']
        
        # ヒストグラムの符号
        df['histogram_sign'] = np.sign(df['histogram'])
        
        # ヒストグラムの符号の変化
        df['histogram_sign_change'] = df['histogram_sign'].diff()
        
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
        
        # 買いシグナル: ヒストグラムが負から正に変化
        buy_condition = df['histogram_sign_change'] == 2  # -1 -> 1
        df['signal'] = np.where(buy_condition, 1.0, df['signal'])
        
        # 売りシグナル: ヒストグラムが正から負に変化
        sell_condition = df['histogram_sign_change'] == -2  # 1 -> -1
        df['signal'] = np.where(sell_condition, -1.0, df['signal'])
        
        # シグナルの変化点を検出
        df['position'] = df['signal'].diff()
        
        # 結果のDataFrameを作成
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['Close']
        signals['macd'] = df['macd']
        signals['signal_line'] = df['signal_line']
        signals['histogram'] = df['histogram']
        signals['histogram_sign'] = df['histogram_sign']
        signals['histogram_sign_change'] = df['histogram_sign_change']
        signals['signal'] = df['signal']
        signals['position'] = df['position']
        
        return signals

class MACDDivergenceStrategy(Strategy):
    """
    MACDダイバージェンス戦略
    
    価格が上昇しているのにMACDが下降している場合は売り（ネガティブダイバージェンス）
    価格が下降しているのにMACDが上昇している場合は買い（ポジティブダイバージェンス）
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初期化
        
        Args:
            params: 戦略パラメータ
                - fast_period: 短期EMAの期間 (デフォルト: 12)
                - slow_period: 長期EMAの期間 (デフォルト: 26)
                - signal_period: シグナルラインの期間 (デフォルト: 9)
                - divergence_period: ダイバージェンス検出期間 (デフォルト: 10)
        """
        default_params = {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'divergence_period': 10
        }
        
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
        
        self.fast_period = self.params['fast_period']
        self.slow_period = self.params['slow_period']
        self.signal_period = self.params['signal_period']
        self.divergence_period = self.params['divergence_period']
    
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
        
        # 短期EMAの計算
        df['ema_fast'] = df['Close'].ewm(span=self.fast_period, adjust=False).mean()
        
        # 長期EMAの計算
        df['ema_slow'] = df['Close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # MACDラインの計算
        df['macd'] = df['ema_fast'] - df['ema_slow']
        
        # シグナルラインの計算
        df['signal_line'] = df['macd'].ewm(span=self.signal_period, adjust=False).mean()
        
        # ヒストグラムの計算
        df['histogram'] = df['macd'] - df['signal_line']
        
        # 価格の傾き
        df['price_slope'] = df['Close'].diff(self.divergence_period)
        
        # MACDの傾き
        df['macd_slope'] = df['macd'].diff(self.divergence_period)
        
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
        
        # ポジティブダイバージェンス: 価格が下降しているのにMACDが上昇
        positive_divergence = (df['price_slope'] < 0) & (df['macd_slope'] > 0)
        df['signal'] = np.where(positive_divergence, 1.0, df['signal'])
        
        # ネガティブダイバージェンス: 価格が上昇しているのにMACDが下降
        negative_divergence = (df['price_slope'] > 0) & (df['macd_slope'] < 0)
        df['signal'] = np.where(negative_divergence, -1.0, df['signal'])
        
        # シグナルの変化点を検出
        df['position'] = df['signal'].diff()
        
        # 結果のDataFrameを作成
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['Close']
        signals['macd'] = df['macd']
        signals['signal_line'] = df['signal_line']
        signals['histogram'] = df['histogram']
        signals['price_slope'] = df['price_slope']
        signals['macd_slope'] = df['macd_slope']
        signals['signal'] = df['signal']
        signals['position'] = df['position']
        
        return signals