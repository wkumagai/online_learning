# 取引モジュール

## 概要
取引モジュールは、戦略から生成されたシグナルを実際の市場注文に変換し、ポジション管理とリスク管理を行うコンポーネントです。ペーパートレード（仮想取引）と実取引の両方をサポートし、様々な取引所やブローカーとの接続を提供します。

## 主要コンポーネント

### 1. 注文管理
- **注文タイプ**: 市場注文、指値注文、逆指値注文、OCO注文など
- **注文ライフサイクル**: 作成、送信、確認、約定、キャンセル
- **注文履歴**: すべての注文の詳細な記録
- **注文バッチ処理**: 複数注文の効率的な処理

### 2. 執行システム
- **ペーパートレード**: 仮想環境での取引シミュレーション
- **実取引**: 実際の市場での注文執行
- **スマート執行**: 最適な執行タイミングと分割注文
- **スリッページモデル**: 現実的な執行コストのモデリング

### 3. ポジション管理
- **ポジショントラッキング**: 現在のポジションの監視
- **ポートフォリオバランス**: 資産配分の管理
- **ポジションサイジング**: リスクに基づいた取引サイズの決定
- **ヘッジ戦略**: リスク軽減のためのヘッジポジション

### 4. リスク管理
- **ストップロス**: 損失を制限するための自動ストップ
- **テイクプロフィット**: 利益確定のための自動注文
- **エクスポージャー制限**: 最大リスク量の制御
- **資金管理**: 適切な資金配分と保護

### 5. ブローカー接続
- **API統合**: 様々なブローカーとの接続
- **認証管理**: セキュアな認証情報の管理
- **レート制限処理**: API制限の遵守
- **フォールバックメカニズム**: 接続問題の処理

## 使用方法

### 基本的な取引実行
```python
from src.trading import trading
from src.trading.execution import paper_executor

# ペーパートレード実行エンジンを初期化
executor = paper_executor.PaperExecutor(
    initial_capital=1000000,
    commission=0.001,
    slippage=0.0005
)

# 戦略からシグナルを取得
signals = my_strategy.generate_signals(data)

# シグナルに基づいて注文を作成
orders = trading.create_orders_from_signals(
    signals=signals,
    position_size=0.1,  # 資本の10%を各ポジションに割り当て
    stop_loss_pct=0.05,  # 5%のストップロス
    take_profit_pct=0.15  # 15%のテイクプロフィット
)

# 注文を実行
execution_results = executor.execute_orders(orders)

# 実行結果を表示
print(execution_results)
```

### 実取引の設定
```python
from src.trading.execution import real_executor
from src.trading.common import trade_executor

# 実取引実行エンジンを初期化
real_engine = real_executor.RealExecutor(
    broker="alpaca",  # 使用するブローカー
    credentials={
        "api_key": "YOUR_API_KEY",
        "api_secret": "YOUR_API_SECRET",
        "base_url": "https://paper-api.alpaca.markets"  # ペーパートレードURL
    },
    risk_limits={
        "max_position_size": 0.1,  # 資本の最大10%
        "max_daily_drawdown": 0.02,  # 最大日次ドローダウン2%
        "max_open_trades": 5  # 最大同時オープンポジション数
    }
)

# 取引実行マネージャーを作成
execution_manager = trade_executor.TradeExecutor(
    executor=real_engine,
    order_manager=order_manager,
    position_manager=position_manager
)

# 戦略を実行マネージャーに接続
execution_manager.connect_strategy(my_strategy)

# 取引を開始
execution_manager.start()
```

### ポジションサイジングとリスク管理
```python
from src.trading.common import strategy_manager

# リスク管理付きの戦略マネージャーを作成
manager = strategy_manager.StrategyManager(
    strategy=my_strategy,
    risk_manager=risk_manager,
    position_sizer=position_sizer
)

# ケリー基準に基づくポジションサイザーを設定
from src.trading.common.position_sizing import kelly
position_sizer = kelly.KellyPositionSizer(
    fraction=0.5,  # ハーフケリー（より保守的）
    win_rate=0.6,  # 勝率60%
    win_loss_ratio=1.5  # 勝ち:負けの比率
)

# リスク管理ルールを設定
manager.set_risk_rules({
    "max_position_size": 0.1,  # 資本の最大10%
    "max_correlated_positions": 0.2,  # 相関資産への最大エクスポージャー20%
    "stop_loss_pct": 0.05,  # 5%のストップロス
    "max_daily_loss": 0.03  # 最大日次損失3%
})

# 取引を実行
manager.execute_trades(data)
```

### 複数戦略の管理
```python
# 複数戦略のポートフォリオを作成
portfolio = trading.create_strategy_portfolio([
    {"strategy": strategy1, "allocation": 0.4},  # 40%の資本配分
    {"strategy": strategy2, "allocation": 0.3},  # 30%の資本配分
    {"strategy": strategy3, "allocation": 0.3}   # 30%の資本配分
])

# ポートフォリオを実行
portfolio_results = trading.execute_portfolio(
    portfolio=portfolio,
    executor=executor,
    data=data
)
```

## 注文タイプ

### 基本注文
- **市場注文**: 現在の市場価格で即時執行
- **指値注文**: 指定価格以下（買い）または以上（売り）で執行
- **逆指値注文**: 指定価格に達したら市場注文として執行

### 高度な注文
- **OCO (One-Cancels-Other)**: 一方が約定すると他方がキャンセル
- **トレーリングストップ**: 価格変動に応じて自動調整されるストップ
- **TWAP/VWAP**: 時間/出来高加重平均価格での執行
- **アイスバーグ注文**: 大口注文を小さな注文に分割

## リスク管理戦略

### ポジションレベル
- **固定ストップロス**: 価格ベースの損失制限
- **ボラティリティストップ**: ATRなどに基づく動的ストップ
- **時間ベースの終了**: 特定期間後の自動終了
- **利益確定**: 段階的な利益確定戦略

### ポートフォリオレベル
- **最大エクスポージャー**: セクター/資産クラスごとの制限
- **相関管理**: 高相関ポジションの制限
- **VaRベースの制限**: バリューアットリスクに基づく制限
- **ドローダウン制御**: 連続損失時の取引サイズ縮小

## 設定
取引設定は `src/system/config.py` と `.env` ファイルで管理されています。主な設定項目：
- ブローカー認証情報
- 取引パラメータ（手数料、スリッページなど）
- リスク管理パラメータ
- 実行モード（ペーパー/実取引）

## 依存関係
- pandas
- numpy
- ccxt (暗号資産取引所接続)
- alpaca-trade-api (米国株式取引)
- Interactive Brokers API (オプション)

## 将来の拡張
- マルチブローカー同時接続
- 高頻度取引サポート
- 取引アルゴリズムの最適化
- 機械学習ベースの執行戦略
- 分散型取引システム