# 戦略モジュール

## 概要
戦略モジュールは、市場データを分析し、取引シグナルを生成するための様々なアルゴリズムとモデルを提供します。テクニカル分析から機械学習まで、多様な戦略アプローチをサポートしています。

## 主要コンポーネント

### 1. 基本戦略フレームワーク
- **基底クラス**: すべての戦略の共通インターフェース
- **イベント処理**: 市場データイベントの処理メカニズム
- **シグナル生成**: 買い/売りシグナルの標準化された生成
- **パラメータ管理**: 戦略パラメータの最適化と管理

### 2. テクニカル分析戦略
- **移動平均戦略**: SMA、EMA、WMAベースの戦略
- **オシレーター戦略**: RSI、ストキャスティクス、MACDベースの戦略
- **ボラティリティ戦略**: ボリンジャーバンド、ATRベースの戦略
- **パターン認識**: チャートパターンに基づく戦略

### 3. 機械学習戦略
- **回帰モデル**: 価格予測のための線形/非線形回帰
- **分類モデル**: 方向性予測のための分類アルゴリズム
- **時系列モデル**: ARIMA、GARCH、LSTMなどの時系列予測
- **強化学習**: Q学習、Deep Q-Network、Actor-Criticモデル

### 4. ハイブリッド戦略
- **テクニカル+機械学習**: テクニカル指標を特徴量とした機械学習
- **アンサンブル手法**: 複数戦略の組み合わせと加重
- **適応型戦略**: 市場状況に応じて戦略を切り替える

### 5. バックテストと最適化
- **パラメータ最適化**: グリッドサーチ、ベイズ最適化
- **ウォークフォワード検証**: 時間依存バイアスの軽減
- **モンテカルロシミュレーション**: 確率的パフォーマンス評価

## 使用方法

### 基本的な使用例
```python
from src.strategy import strategy
from src.strategy.models.Technical import moving_average

# 移動平均クロスオーバー戦略を作成
ma_strategy = moving_average.MovingAverageCrossover(
    fast_period=10,
    slow_period=30,
    price_column='close'
)

# 戦略を初期化
ma_strategy.initialize(data)

# シグナルを生成
signals = ma_strategy.generate_signals()

# 戦略のパフォーマンスを評価
performance = strategy.evaluate_strategy(
    strategy=ma_strategy,
    data=data,
    initial_capital=1000000,
    commission=0.001
)
```

### 機械学習戦略の例
```python
from src.strategy.models.ML import deep_learning

# 特徴量を定義
features = [
    'sma_10', 'sma_30', 'rsi_14', 'macd', 'volume', 
    'day_of_week', 'month', 'volatility'
]

# LSTM戦略を作成
lstm_strategy = deep_learning.LSTMStrategy(
    features=features,
    target='return_next_day',
    lookback_period=20,
    hidden_units=64,
    dropout=0.2
)

# モデルを訓練
lstm_strategy.train(
    train_data=train_data,
    validation_data=validation_data,
    epochs=100,
    batch_size=32
)

# シグナルを生成
signals = lstm_strategy.generate_signals(test_data)
```

### 戦略の最適化
```python
from src.strategy import optimizer

# 最適化パラメータを定義
params_space = {
    'fast_period': range(5, 21),
    'slow_period': range(20, 101, 5),
    'signal_period': range(5, 16)
}

# 最適化を実行
best_params = optimizer.grid_search(
    strategy_class=moving_average.MACD,
    params_space=params_space,
    data=data,
    metric='sharpe_ratio',
    cv=5  # 5分割クロスバリデーション
)

# 最適化された戦略を作成
optimized_strategy = moving_average.MACD(**best_params)
```

## 戦略開発ガイドライン

### 新しい戦略の追加
1. 適切なカテゴリ（Technical、ML、Hybrid）を選択
2. 基底クラス（BaseStrategy）を継承
3. 必要なメソッドをオーバーライド（initialize、generate_signals、update）
4. ユニットテストを作成
5. バックテストで戦略を検証

### パフォーマンス最適化
- 計算集約的な処理はNumPyベクトル化操作を使用
- 大規模データセットにはメモリマッピングを検討
- 並列処理を活用（特に最適化とシミュレーション）
- キャッシュを適切に使用

## 依存関係
- pandas
- numpy
- scikit-learn
- tensorflow/keras
- pytorch (オプション)
- ta-lib (テクニカル指標)

## 将来の拡張
- マルチアセット戦略
- 市場間アービトラージ
- センチメント分析統合
- 遺伝的アルゴリズムによる戦略進化
- 説明可能なAIアプローチ