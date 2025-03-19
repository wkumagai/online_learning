"""
strategy.py

戦略ロジックの管理（検索・学習・シグナル生成など）を行うモジュール。
"""

import os
import json
import logging
import datetime
import time
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
import pickle
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model, save_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# ロギングの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ファイルハンドラの設定
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = logging.FileHandler('logs/strategy.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# コンソールハンドラの設定
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)


class Strategy:
    """戦略の基本クラス"""
    
    def __init__(self, name: str, description: str = ""):
        """
        Parameters:
        -----------
        name : str
            戦略の名前
        description : str, optional
            戦略の説明
        """
        self.name = name
        self.description = description
        self.parameters = {}
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        
    def generate_signal(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        株価データから売買シグナルを生成する
        
        Parameters:
        -----------
        data : pd.DataFrame
            株価データ
        
        Returns:
        --------
        pd.DataFrame
            シグナルが追加されたデータフレーム
        """
        # 派生クラスでオーバーライドする
        raise NotImplementedError("派生クラスで実装する必要があります")
    
    def save(self, directory: str = "data/strategy/models") -> str:
        """
        戦略を保存する
        
        Parameters:
        -----------
        directory : str, optional
            保存先ディレクトリ
        
        Returns:
        --------
        str
            保存したファイルのパス
        """
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, f"{self.name}.json")
        
        # 保存用のデータを作成
        save_data = {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "type": self.__class__.__name__,
            "created_at": self.created_at.isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
        
        # JSONに保存
        with open(file_path, "w") as f:
            json.dump(save_data, f, indent=2)
        
        logger.info(f"戦略を保存しました: {file_path}")
        return file_path
    
    @classmethod
    def load(cls, file_path: str) -> 'Strategy':
        """
        保存された戦略を読み込む
        
        Parameters:
        -----------
        file_path : str
            読み込むファイルのパス
        
        Returns:
        --------
        Strategy
            読み込んだ戦略
        """
        # JSONから読み込み
        with open(file_path, "r") as f:
            data = json.load(f)
        
        # 戦略の種類に応じたインスタンスを作成
        strategy_type = data.get("type", "Strategy")
        
        if strategy_type == "MovingAverageStrategy":
            strategy = MovingAverageStrategy(data["name"], data["description"])
        elif strategy_type == "RSIStrategy":
            strategy = RSIStrategy(data["name"], data["description"])
        elif strategy_type == "MachineLearningStrategy":
            strategy = MachineLearningStrategy(data["name"], data["description"])
        elif strategy_type == "LSTMStrategy":
            strategy = LSTMStrategy(data["name"], data["description"])
        elif strategy_type == "NewsBasedStrategy":
            strategy = NewsBasedStrategy(data["name"], data["description"])
        else:
            strategy = Strategy(data["name"], data["description"])
        
        # パラメータの設定
        strategy.parameters = data.get("parameters", {})
        strategy.created_at = datetime.datetime.fromisoformat(data.get("created_at", datetime.datetime.now().isoformat()))
        strategy.updated_at = datetime.datetime.fromisoformat(data.get("updated_at", datetime.datetime.now().isoformat()))
        
        logger.info(f"戦略を読み込みました: {file_path}")
        return strategy


class MovingAverageStrategy(Strategy):
    """移動平均を使用した戦略"""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.parameters = {
            "short_window": 5,
            "long_window": 20,
            "signal_threshold": 0
        }
    
    def generate_signal(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        移動平均の交差に基づいて売買シグナルを生成する
        
        Parameters:
        -----------
        data : pd.DataFrame
            株価データ
        
        Returns:
        --------
        pd.DataFrame
            シグナルが追加されたデータフレーム
        """
        # パラメータの取得
        short_window = self.parameters.get("short_window", 5)
        long_window = self.parameters.get("long_window", 20)
        signal_threshold = self.parameters.get("signal_threshold", 0)
        
        # データのコピーを作成
        df = data.copy()
        
        # 必要なカラムの存在確認
        if "close" not in df.columns:
            logger.error("データに'close'カラムがありません")
            return df
        
        # 移動平均の計算
        if f"sma_{short_window}" not in df.columns:
            df[f"sma_{short_window}"] = df["close"].rolling(window=short_window).mean()
        
        if f"sma_{long_window}" not in df.columns:
            df[f"sma_{long_window}"] = df["close"].rolling(window=long_window).mean()
        
        # シグナルの生成
        df["signal"] = 0
        
        # 短期移動平均が長期移動平均を上回る（ゴールデンクロス）→ 買いシグナル
        df.loc[df[f"sma_{short_window}"] > df[f"sma_{long_window}"] + signal_threshold, "signal"] = 1
        
        # 短期移動平均が長期移動平均を下回る（デッドクロス）→ 売りシグナル
        df.loc[df[f"sma_{short_window}"] < df[f"sma_{long_window}"] - signal_threshold, "signal"] = -1
        
        # NaNの処理
        df["signal"] = df["signal"].fillna(0)
        
        logger.info(f"移動平均戦略によるシグナル生成完了: {self.name}")
        return df


class RSIStrategy(Strategy):
    """RSI（相対力指数）を使用した戦略"""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.parameters = {
            "rsi_period": 14,
            "overbought": 70,
            "oversold": 30
        }
    
    def generate_signal(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        RSIに基づいて売買シグナルを生成する
        
        Parameters:
        -----------
        data : pd.DataFrame
            株価データ
        
        Returns:
        --------
        pd.DataFrame
            シグナルが追加されたデータフレーム
        """
        # パラメータの取得
        rsi_period = self.parameters.get("rsi_period", 14)
        overbought = self.parameters.get("overbought", 70)
        oversold = self.parameters.get("oversold", 30)
        
        # データのコピーを作成
        df = data.copy()
        
        # 必要なカラムの存在確認
        if "close" not in df.columns:
            logger.error("データに'close'カラムがありません")
            return df
        
        # RSIの計算
        if "rsi" not in df.columns:
            delta = df["close"].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=rsi_period).mean()
            avg_loss = loss.rolling(window=rsi_period).mean()
            rs = avg_gain / avg_loss
            df["rsi"] = 100 - (100 / (1 + rs))
        
        # シグナルの生成
        df["signal"] = 0
        
        # RSIが過売り水準を下回る → 買いシグナル
        df.loc[df["rsi"] < oversold, "signal"] = 1
        
        # RSIが過買い水準を上回る → 売りシグナル
        df.loc[df["rsi"] > overbought, "signal"] = -1
        
        # NaNの処理
        df["signal"] = df["signal"].fillna(0)
        
        logger.info(f"RSI戦略によるシグナル生成完了: {self.name}")
        return df


class MachineLearningStrategy(Strategy):
    """機械学習を使用した戦略"""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.parameters = {
            "model_type": "random_forest",  # random_forest, gradient_boosting
            "prediction_horizon": 1,  # 何日先を予測するか
            "features": ["sma_5", "sma_20", "rsi", "macd", "macd_signal", "bb_upper", "bb_lower"],
            "train_test_split": 0.2,
            "signal_threshold": 0.5
        }
        self.model = None
        self.scaler = None
    
    def generate_signal(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        機械学習モデルに基づいて売買シグナルを生成する
        
        Parameters:
        -----------
        data : pd.DataFrame
            株価データ
        
        Returns:
        --------
        pd.DataFrame
            シグナルが追加されたデータフレーム
        """
        # モデルが学習済みかチェック
        if self.model is None:
            logger.error("モデルが学習されていません")
            return data
        
        # データのコピーを作成
        df = data.copy()
        
        # 特徴量の抽出
        features = self.parameters.get("features", [])
        X = df[features].values
        
        # 特徴量のスケーリング
        if self.scaler is not None:
            X = self.scaler.transform(X)
        
        # 予測
        if self.parameters.get("model_type") == "random_forest":
            # 分類モデルの場合
            predictions = self.model.predict_proba(X)[:, 1]  # クラス1（上昇）の確率
        else:
            # 回帰モデルの場合
            predictions = self.model.predict(X)
        
        # シグナルの生成
        df["prediction"] = predictions
        df["signal"] = 0
        
        # 予測値が閾値を超える → 買いシグナル
        threshold = self.parameters.get("signal_threshold", 0.5)
        df.loc[df["prediction"] > threshold, "signal"] = 1
        
        # 予測値が閾値を下回る → 売りシグナル
        df.loc[df["prediction"] < (1 - threshold), "signal"] = -1
        
        logger.info(f"機械学習戦略によるシグナル生成完了: {self.name}")
        return df
    
    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        機械学習モデルを学習する
        
        Parameters:
        -----------
        data : pd.DataFrame
            学習データ
        
        Returns:
        --------
        Dict[str, Any]
            学習結果
        """
        # パラメータの取得
        model_type = self.parameters.get("model_type", "random_forest")
        features = self.parameters.get("features", [])
        prediction_horizon = self.parameters.get("prediction_horizon", 1)
        test_size = self.parameters.get("train_test_split", 0.2)
        
        # データの準備
        df = data.copy()
        
        # 目的変数の作成（n日後の価格が上昇するかどうか）
        df["target"] = (df["close"].shift(-prediction_horizon) > df["close"]).astype(int)
        
        # NaNの削除
        df = df.dropna()
        
        # 特徴量と目的変数の抽出
        X = df[features].values
        y = df["target"].values
        
        # 学習データとテストデータの分割
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)
        
        # 特徴量のスケーリング
        self.scaler = StandardScaler()
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        
        # モデルの選択と学習
        if model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.model.fit(X_train, y_train)
            
            # テストデータでの評価
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            logger.info(f"ランダムフォレストモデルの学習完了: {self.name}")
            logger.info(f"精度: {accuracy:.4f}, 適合率: {precision:.4f}, 再現率: {recall:.4f}, F1スコア: {f1:.4f}")
            
            return {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "feature_importance": dict(zip(features, self.model.feature_importances_))
            }
            
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
            self.model.fit(X_train, y_train)
            
            # テストデータでの評価
            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            logger.info(f"勾配ブースティングモデルの学習完了: {self.name}")
            logger.info(f"RMSE: {rmse:.4f}")
            
            return {
                "mse": mse,
                "rmse": rmse,
                "feature_importance": dict(zip(features, self.model.feature_importances_))
            }
        
        else:
            logger.error(f"未対応のモデルタイプ: {model_type}")
            return {}
    
    def save_model(self, directory: str = "data/strategy/models") -> str:
        """
        学習済みモデルを保存する
        
        Parameters:
        -----------
        directory : str, optional
            保存先ディレクトリ
        
        Returns:
        --------
        str
            保存したファイルのパス
        """
        if self.model is None:
            logger.error("保存するモデルがありません")
            return ""
        
        # ディレクトリの作成
        model_dir = os.path.join(directory, self.name)
        os.makedirs(model_dir, exist_ok=True)
        
        # モデルの保存
        model_path = os.path.join(model_dir, "model.joblib")
        joblib.dump(self.model, model_path)
        
        # スケーラーの保存
        if self.scaler is not None:
            scaler_path = os.path.join(model_dir, "scaler.joblib")
            joblib.dump(self.scaler, scaler_path)
        
        # 設定の保存
        config_path = os.path.join(model_dir, "config.json")
        with open(config_path, "w") as f:
            json.dump({
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
                "type": self.__class__.__name__,
                "created_at": self.created_at.isoformat(),
                "updated_at": datetime.datetime.now().isoformat()
            }, f, indent=2)
        
        logger.info(f"モデルを保存しました: {model_dir}")
        return model_dir
    
    @classmethod
    def load_model(cls, directory: str) -> 'MachineLearningStrategy':
        """
        保存されたモデルを読み込む
        
        Parameters:
        -----------
        directory : str
            モデルが保存されているディレクトリ
        
        Returns:
        --------
        MachineLearningStrategy
            読み込んだモデル
        """
        # 設定の読み込み
        config_path = os.path.join(directory, "config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # 戦略の作成
        strategy = cls(config["name"], config["description"])
        strategy.parameters = config["parameters"]
        strategy.created_at = datetime.datetime.fromisoformat(config["created_at"])
        strategy.updated_at = datetime.datetime.fromisoformat(config["updated_at"])
        
        # モデルの読み込み
        model_path = os.path.join(directory, "model.joblib")
        strategy.model = joblib.load(model_path)
        
        # スケーラーの読み込み
        scaler_path = os.path.join(directory, "scaler.joblib")
        if os.path.exists(scaler_path):
            strategy.scaler = joblib.load(scaler_path)
        
        logger.info(f"モデルを読み込みました: {directory}")
        return strategy


class LSTMStrategy(Strategy):
    """LSTMを使用した戦略"""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.parameters = {
            "sequence_length": 10,
            "prediction_horizon": 1,
            "features": ["close", "volume", "rsi", "macd"],
            "lstm_units": [64, 32],
            "dropout_rate": 0.2,
            "epochs": 50,
            "batch_size": 32,
            "train_test_split": 0.2,
            "signal_threshold": 0.01
        }
        self.model = None
        self.scaler = None
    
    def generate_signal(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        LSTMモデルに基づいて売買シグナルを生成する
        
        Parameters:
        -----------
        data : pd.DataFrame
            株価データ
        
        Returns:
        --------
        pd.DataFrame
            シグナルが追加されたデータフレーム
        """
        # モデルが学習済みかチェック
        if self.model is None:
            logger.error("モデルが学習されていません")
            return data
        
        # データのコピーを作成
        df = data.copy()
        
        # パラメータの取得
        sequence_length = self.parameters.get("sequence_length", 10)
        features = self.parameters.get("features", [])
        
        # 特徴量の抽出
        X = df[features].values
        
        # 特徴量のスケーリング
        if self.scaler is not None:
            X = self.scaler.transform(X)
        
        # シーケンスデータの作成
        X_sequences = []
        for i in range(len(X) - sequence_length + 1):
            X_sequences.append(X[i:i+sequence_length])
        
        X_sequences = np.array(X_sequences)
        
        # 予測
        predictions = self.model.predict(X_sequences)
        
        # 予測結果をデータフレームに追加
        df["prediction"] = np.nan
        df.loc[sequence_length-1:sequence_length-1+len(predictions), "prediction"] = predictions.flatten()
        
        # シグナルの生成
        df["signal"] = 0
        threshold = self.parameters.get("signal_threshold", 0.01)
        
        # 予測値が閾値を超える → 買いシグナル
        df.loc[df["prediction"] > threshold, "signal"] = 1
        
        # 予測値が閾値を下回る → 売りシグナル
        df.loc[df["prediction"] < -threshold, "signal"] = -1
        
        logger.info(f"LSTM戦略によるシグナル生成完了: {self.name}")
        return df
    
    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        LSTMモデルを学習する
        
        Parameters:
        -----------
        data : pd.DataFrame
            学習データ
        
        Returns:
        --------
        Dict[str, Any]
            学習結果
        """
        # パラメータの取得
        sequence_length = self.parameters.get("sequence_length", 10)
        prediction_horizon = self.parameters.get("prediction_horizon", 1)
        features = self.parameters.get("features", [])
        lstm_units = self.parameters.get("lstm_units", [64, 32])
        dropout_rate = self.parameters.get("dropout_rate", 0.2)
        epochs = self.parameters.get("epochs", 50)
        batch_size = self.parameters.get("batch_size", 32)
        test_size = self.parameters.get("train_test_split", 0.2)
        
        # データの準備
        df = data.copy()
        
        # 目的変数の作成（n日後のリターン）
        df["target"] = df["close"].pct_change(prediction_horizon).shift(-prediction_horizon)
        
        # NaNの削除
        df = df.dropna()
        
        # 特徴量と目的変数の抽出
        X = df[features].values
        y = df["target"].values
        
        # 特徴量のスケーリング
        self.scaler = StandardScaler()
        X = self.scaler.fit_transform(X)
        
        # シーケンスデータの作成
        X_sequences = []
        y_values = []
        
        for i in range(len(X) - sequence_length - prediction_horizon + 1):
            X_sequences.append(X[i:i+sequence_length])
            y_values.append(y[i+sequence_length-1])
        
        X_sequences = np.array(X_sequences)
        y_values = np.array(y_values)
        
        # 学習データとテストデータの分割
        split_idx = int(len(X_sequences) * (1 - test_size))
        X_train, X_test = X_sequences[:split_idx], X_sequences[split_idx:]
        y_train, y_test = y_values[:split_idx], y_values[split_idx:]
        
        # モデルの構築
        self.model = Sequential()
        
        # LSTM層の追加
        for i, units in enumerate(lstm_units):
            return_sequences = i < len(lstm_units) - 1
            if i == 0:
                self.model.add(LSTM(units, return_sequences=return_sequences, input_shape=(sequence_length, len(features))))
            else:
                self.model.add(LSTM(units, return_sequences=return_sequences))
            self.model.add(Dropout(dropout_rate))
        
        # 出力層
        self.model.add(Dense(1))
        
        # モデルのコンパイル
        self.model.compile(optimizer=Adam(), loss='mse')
        
        # コールバックの設定
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        ]
        
        # モデルの学習
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_test, y_test),
            callbacks=callbacks,
            verbose=1
        )
        
        # テストデータでの評価
        test_loss = self.model.evaluate(X_test, y_test, verbose=0)
        y_pred = self.model.predict(X_test).flatten()
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        logger.info(f"LSTMモデルの学習完了: {self.name}")
        logger.info(f"テスト損失: {test_loss:.4f}, RMSE: {rmse:.4f}")
        
        return {
            "test_loss": test_loss,
            "mse": mse,
            "rmse": rmse,
            "history": history.history
        }
    
    def save_model(self, directory: str = "data/strategy/models") -> str:
        """
        学習済みモデルを保存する
        
        Parameters:
        -----------
        directory : str, optional
            保存先ディレクトリ
        
        Returns:
        --------
        str
            保存したファイルのパス
        """
        if self.model is None:
            logger.error("保存するモデルがありません")
            return ""
        
        # ディレクトリの作成
        model_dir = os.path.join(directory, self.name)
        os.makedirs(model_dir, exist_ok=True)
        
        # モデルの保存
        model_path = os.path.join(model_dir, "model.keras")
        self.model.save(model_path)
        
        # スケーラーの保存
        if self.scaler is not None:
            scaler_path = os.path.join(model_dir, "scaler.joblib")
            joblib.dump(self.scaler, scaler_path)
        
        # 設定の保存
        config_path = os.path.join(model_dir, "config.json")
        with open(config_path, "w") as f:
            json.dump({
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
                "type": self.__class__.__name__,
                "created_at": self.created_at.isoformat(),
                "updated_at": datetime.datetime.now().isoformat()
            }, f, indent=2)
        
        logger.info(f"モデルを保存しました: {model_dir}")
        return model_dir
    
    @classmethod
    def load_model(cls, directory: str) -> 'LSTMStrategy':
        """
        保存されたモデルを読み込む
        
        Parameters:
        -----------
        directory : str
            モデルが保存されているディレクトリ
        
        Returns:
        --------
        LSTMStrategy
            読み込んだモデル
        """
        # 設定の読み込み
        config_path = os.path.join(directory, "config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # 戦略の作成
        strategy = cls(config["name"], config["description"])
        strategy.parameters = config["parameters"]
        strategy.created_at = datetime.datetime.fromisoformat(config["created_at"])
        strategy.updated_at = datetime.datetime.fromisoformat(config["updated_at"])
        
        # モデルの読み込み
        model_path = os.path.join(directory, "model.keras")
        strategy.model = load_model(model_path)
        
        # スケーラーの読み込み
        scaler_path = os.path.join(directory, "scaler.joblib")
        if os.path.exists(scaler_path):
            strategy.scaler = joblib.load(scaler_path)
        
        logger.info(f"モデルを読み込みました: {directory}")
        return strategy


class NewsBasedStrategy(Strategy):
    """ニュース情報を使用した戦略"""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.parameters = {
            "sentiment_threshold_positive": 0.5,
            "sentiment_threshold_negative": -0.5,
            "news_window": 3,  # ニュースの影響を考慮する日数
            "signal_strength": 0.5  # シグナルの強さ（0-1）
        }
    
    def generate_signal(self, data: pd.DataFrame, news_data: List[Dict] = None) -> pd.DataFrame:
        """
        ニュース感情分析に基づいて売買シグナルを生成する
        
        Parameters:
        -----------
        data : pd.DataFrame
            株価データ
        news_data : List[Dict], optional
            ニュースデータ
        
        Returns:
        --------
        pd.DataFrame
            シグナルが追加されたデータフレーム
        """
        # データのコピーを作成
        df = data.copy()
        
        # ニュースデータがない場合
        if news_data is None or len(news_data) == 0:
            logger.warning("ニュースデータがありません")
            df["signal"] = 0
            return df
        
        # パラメータの取得
        pos_threshold = self.parameters.get("sentiment_threshold_positive", 0.5)
        neg_threshold = self.parameters.get("sentiment_threshold_negative", -0.5)
        news_window = self.parameters.get("news_window", 3)
        signal_strength = self.parameters.get("signal_strength", 0.5)
        
        # 日付列の確認
        if "date" not in df.columns:
            logger.error("データに'date'カラムがありません")
            return df
        
        # ニュースの日付を日時型に変換
        for news in news_data:
            if "published_at" in news:
                news["date"] = pd.to_datetime(news["published_at"])
        
        # 各日付のニュース感情スコアを計算
        df["news_sentiment"] = 0.0
        
        for i, row in df.iterrows():
            date = row["date"]
            
            # 指定した日数内のニュースを抽出
            relevant_news = [
                news for news in news_data
                if "date" in news and abs((news["date"] - date).days) <= news_window
            ]
            
            # ニュースの感情スコアの平均を計算
            if relevant_news:
                sentiment_scores = [
                    news.get("sentiment", {}).get("score", 0)
                    for news in relevant_news
                ]
                df.at[i, "news_sentiment"] = np.mean(sentiment_scores)
        
        # シグナルの生成
        df["signal"] = 0
        
        # ポジティブなニュース → 買いシグナル
        df.loc[df["news_sentiment"] > pos_threshold, "signal"] = 1 * signal_strength
        
        # ネガティブなニュース → 売りシグナル
        df.loc[df["news_sentiment"] < neg_threshold, "signal"] = -1 * signal_strength
        
        logger.info(f"ニュース戦略によるシグナル生成完了: {self.name}")
        return df


def load_existing_strategies(directory: str = "data/strategy/models") -> Dict[str, Strategy]:
    """
    既存の戦略を読み込む関数
    
    Parameters:
    -----------
    directory : str, optional
        戦略が保存されているディレクトリ
    
    Returns:
    --------
    Dict[str, Strategy]
        読み込んだ戦略の辞書
    """
    strategies = {}
    
    # ディレクトリの存在確認
    if not os.path.exists(directory):
        logger.warning(f"ディレクトリが存在しません: {directory}")
        return strategies
    
    # JSONファイルの検索
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    
    for json_file in json_files:
        try:
            file_path = os.path.join(directory, json_file)
            strategy = Strategy.load(file_path)
            strategies[strategy.name] = strategy
            logger.info(f"戦略を読み込みました: {strategy.name}")
        except Exception as e:
            logger.error(f"戦略の読み込みエラー: {json_file} - {str(e)}")
    
    # サブディレクトリの検索（機械学習モデル）
    subdirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    
    for subdir in subdirs:
        try:
            dir_path = os.path.join(directory, subdir)
            config_path = os.path.join(dir_path, "config.json")
            
            if os.path.exists(config_path):
                # 設定ファイルの読み込み
                with open(config_path, "r") as f:
                    config = json.load(f)
                
                # 戦略の種類に応じた読み込み
                strategy_type = config.get("type")
                
                if strategy_type == "MachineLearningStrategy":
                    strategy = MachineLearningStrategy.load_model(dir_path)
                    strategies[strategy.name] = strategy
                    logger.info(f"機械学習戦略を読み込みました: {strategy.name}")
                
                elif strategy_type == "LSTMStrategy":
                    strategy = LSTMStrategy.load_model(dir_path)
                    strategies[strategy.name] = strategy
                    logger.info(f"LSTM戦略を読み込みました: {strategy.name}")
        
        except Exception as e:
            logger.error(f"モデルの読み込みエラー: {subdir} - {str(e)}")
    
    logger.info(f"合計 {len(strategies)} 個の戦略を読み込みました")
    return strategies


def create_new_strategy(
    strategy_type: str,
    name: str,
    description: str = "",
    parameters: Dict[str, Any] = None
) -> Strategy:
    """
    新しい戦略を作成する関数
    
    Parameters:
    -----------
    strategy_type : str
        戦略の種類（"moving_average", "rsi", "machine_learning", "lstm", "news"）
    name : str
        戦略の名前
    description : str, optional
        戦略の説明
    parameters : Dict[str, Any], optional
        戦略のパラメータ
    
    Returns:
    --------
    Strategy
        作成した戦略
    """
    # 戦略の種類に応じたインスタンスを作成
    if strategy_type == "moving_average":
        strategy = MovingAverageStrategy(name, description)
    elif strategy_type == "rsi":
        strategy = RSIStrategy(name, description)
    elif strategy_type == "machine_learning":
        strategy = MachineLearningStrategy(name, description)
    elif strategy_type == "lstm":
        strategy = LSTMStrategy(name, description)
    elif strategy_type == "news":
        strategy = NewsBasedStrategy(name, description)
    else:
        logger.error(f"未対応の戦略タイプ: {strategy_type}")
        return None
    
    # パラメータの設定
    if parameters:
        strategy.parameters.update(parameters)
    
    logger.info(f"新しい戦略を作成しました: {name} ({strategy_type})")
    return strategy


def model_training(
    strategy: Union[MachineLearningStrategy, LSTMStrategy],
    data: pd.DataFrame
) -> Dict[str, Any]:
    """
    モデルの学習を行う関数
    
    Parameters:
    -----------
    strategy : Union[MachineLearningStrategy, LSTMStrategy]
        学習する戦略
    data : pd.DataFrame
        学習データ
    
    Returns:
    --------
    Dict[str, Any]
        学習結果
    """
    # 戦略の種類に応じた学習
    if isinstance(strategy, MachineLearningStrategy):
        logger.info(f"機械学習戦略の学習を開始します: {strategy.name}")
        results = strategy.train(data)
        strategy.save_model()
        return results
    
    elif isinstance(strategy, LSTMStrategy):
        logger.info(f"LSTM戦略の学習を開始します: {strategy.name}")
        results = strategy.train(data)
        strategy.save_model()
        return results
    
    else:
        logger.error(f"学習に対応していない戦略タイプです: {strategy.__class__.__name__}")
        return {}


def generate_signal(
    strategy: Strategy,
    data: pd.DataFrame,
    news_data: List[Dict] = None
) -> pd.DataFrame:
    """
    戦略に基づいて売買シグナルを生成する関数
    
    Parameters:
    -----------
    strategy : Strategy
        使用する戦略
    data : pd.DataFrame
        株価データ
    news_data : List[Dict], optional
        ニュースデータ（ニュース戦略の場合）
    
    Returns:
    --------
    pd.DataFrame
        シグナルが追加されたデータフレーム
    """
    logger.info(f"シグナル生成を開始します: {strategy.name}")
    
    # 戦略の種類に応じたシグナル生成
    if isinstance(strategy, NewsBasedStrategy) and news_data is not None:
        return strategy.generate_signal(data, news_data)
    else:
        return strategy.generate_signal(data)


def safe_rule_check(
    signals: pd.DataFrame,
    rules: Dict[str, Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    safe-ruleを適用して最終シグナルを補正する関数
    
    Parameters:
    -----------
    signals : pd.DataFrame
        シグナルが含まれるデータフレーム
    rules : Dict[str, Dict[str, Any]], optional
        適用するルール
    
    Returns:
    --------
    pd.DataFrame
        補正されたシグナルが含まれるデータフレーム
    """
    # データのコピーを作成
    df = signals.copy()
    
    # ルールが指定されていない場合はデフォルトルールを使用
    if rules is None:
        rules = {
            "crash_protection": {
                "enabled": True,
                "daily_return_threshold": -0.05,  # 5%以上の下落
                "action": "exit_all"  # 全ポジション清算
            },
            "volatility_limit": {
                "enabled": True,
                "atr_threshold": 0.03,  # ATRが3%以上
                "action": "reduce_position"  # ポジションサイズ縮小
            },
            "trend_filter": {
                "enabled": True,
                "sma_period": 200,  # 200日移動平均
                "action": "follow_trend"  # トレンドに従う
            }
        }
    
    logger.info("safe-ruleの適用を開始します")
    
    # 必要なカラムの存在確認
    required_columns = ["date", "close", "signal"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        logger.error(f"必須カラムがありません: {missing_columns}")
        return df
    
    # 暴落保護ルール
    if rules.get("crash_protection", {}).get("enabled", False):
        threshold = rules["crash_protection"].get("daily_return_threshold", -0.05)
        
        # 日次リターンの計算
        if "daily_return" not in df.columns:
            df["daily_return"] = df["close"].pct_change()
        
        # 暴落の検出
        crash_days = df["daily_return"] < threshold
        
        if crash_days.any():
            logger.warning(f"暴落を検出しました: {crash_days.sum()}日")
            
            action = rules["crash_protection"].get("action", "exit_all")
            
            if action == "exit_all":
                # 全ポジション清算（売りシグナル）
                df.loc[crash_days, "signal"] = -1
                logger.info("暴落保護: 全ポジション清算シグナルを設定しました")
            
            elif action == "no_entry":
                # 新規エントリー禁止（買いシグナルをキャンセル）
                df.loc[crash_days & (df["signal"] > 0), "signal"] = 0
                logger.info("暴落保護: 新規エントリー禁止を設定しました")
    
    # ボラティリティ制限ルール
    if rules.get("volatility_limit", {}).get("enabled", False):
        threshold = rules["volatility_limit"].get("atr_threshold", 0.03)
        
        # ATRの確認
        if "atr" not in df.columns:
            logger.warning("ATRカラムがありません。ボラティリティ制限ルールをスキップします。")
        else:
            # 高ボラティリティの検出
            high_vol_days = df["atr"] / df["close"] > threshold
            
            if high_vol_days.any():
                logger.warning(f"高ボラティリティを検出しました: {high_vol_days.sum()}日")
                
                action = rules["volatility_limit"].get("action", "reduce_position")
                
                if action == "reduce_position":
                    # ポジションサイズ縮小（シグナルを半分に）
                    df.loc[high_vol_days, "signal"] = df.loc[high_vol_days, "signal"] * 0.5
                    logger.info("ボラティリティ制限: ポジションサイズ縮小を設定しました")
                
                elif action == "no_trade":
                    # 取引禁止（シグナルをゼロに）
                    df.loc[high_vol_days, "signal"] = 0
                    logger.info("ボラティリティ制限: 取引禁止を設定しました")
    
    # トレンドフィルタールール
    if rules.get("trend_filter", {}).get("enabled", False):
        period = rules["trend_filter"].get("sma_period", 200)
        
        # 移動平均の計算
        sma_col = f"sma_{period}"
        if sma_col not in df.columns:
            df[sma_col] = df["close"].rolling(window=period).mean()
        
        # トレンドの判定
        df["trend"] = 0
        df.loc[df["close"] > df[sma_col], "trend"] = 1  # 上昇トレンド
        df.loc[df["close"] < df[sma_col], "trend"] = -1  # 下降トレンド
        
        action = rules["trend_filter"].get("action", "follow_trend")
        
        if action == "follow_trend":
            # トレンドに反するシグナルを無効化
            df.loc[(df["trend"] > 0) & (df["signal"] < 0), "signal"] = 0  # 上昇トレンド中の売りシグナルを無効化
            df.loc[(df["trend"] < 0) & (df["signal"] > 0), "signal"] = 0  # 下降トレンド中の買いシグナルを無効化
            logger.info("トレンドフィルター: トレンドに反するシグナルを無効化しました")
        
        elif action == "strengthen_trend":
            # トレンドに沿ったシグナルを強化
            df.loc[(df["trend"] > 0) & (df["signal"] > 0), "signal"] = df.loc[(df["trend"] > 0) & (df["signal"] > 0), "signal"] * 1.5  # 上昇トレンド中の買いシグナルを強化
            df.loc[(df["trend"] < 0) & (df["signal"] < 0), "signal"] = df.loc[(df["trend"] < 0) & (df["signal"] < 0), "signal"] * 1.5  # 下降トレンド中の売りシグナルを強化
            logger.info("トレンドフィルター: トレンドに沿ったシグナルを強化しました")
    
    logger.info("safe-ruleの適用が完了しました")
    return df


if __name__ == "__main__":
    # 動作確認用のコード
    logger.info("strategy.py の動作確認を開始します")
    
    # 既存の戦略の読み込み
    strategies = load_existing_strategies()
    
    if strategies:
        logger.info(f"読み込んだ戦略: {list(strategies.keys())}")
    else:
        # 新しい戦略の作成
        ma_strategy = create_new_strategy(
            strategy_type="moving_average",
            name="SimpleMA",
            description="単純な移動平均戦略",
            parameters={"short_window": 5, "long_window": 20}
        )
        
        rsi_strategy = create_new_strategy(
            strategy_type="rsi",
            name="RSI30_70",
            description="RSIが30/70の閾値を使用する戦略",
            parameters={"rsi_period": 14, "overbought": 70, "oversold": 30}
        )
        
        # 戦略の保存
        ma_strategy.save()
        rsi_strategy.save()
        
        logger.info("新しい戦略を作成して保存しました")
    
    logger.info("strategy.py の動作確認を終了します")