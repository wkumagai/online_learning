# 評価モジュール

## 概要
評価モジュールは、取引戦略のパフォーマンスを包括的に分析し、リスクとリターンの指標を計算するためのツールを提供します。バックテスト評価とリアルタイム評価の両方をサポートし、戦略の有効性を様々な市場条件下で検証します。

## 主要コンポーネント

### 1. バックテスト評価
- **ヒストリカルシミュレーション**: 過去のデータを使用した戦略のシミュレーション
- **パフォーマンス指標**: リターン、シャープレシオ、最大ドローダウンなどの計算
- **取引統計**: 勝率、平均利益/損失、取引回数などの分析
- **マルチタイムフレーム分析**: 様々な時間枠での戦略評価

### 2. リアルタイム評価
- **ライブパフォーマンストラッキング**: リアルタイムでの戦略パフォーマンス監視
- **予測精度評価**: 予測と実際の市場動向の比較
- **アラート生成**: パフォーマンス閾値に基づくアラート
- **適応型評価**: 変化する市場条件に対する戦略の適応性評価

### 3. リスク分析
- **ボラティリティ指標**: 標準偏差、半分散、VaRなど
- **ドローダウン分析**: 深さ、期間、回復時間
- **ストレステスト**: 極端な市場条件下でのシミュレーション
- **相関分析**: 他の戦略や市場指標との相関

### 4. 戦略比較
- **ベンチマーク比較**: 市場指標や他の戦略との比較
- **統計的有意性テスト**: パフォーマンスの統計的検証
- **リスク調整済みパフォーマンス**: リスクを考慮した比較
- **一貫性評価**: 様々な期間や市場条件での一貫性

### 5. 可視化
- **パフォーマンスチャート**: 累積リターン、ドローダウン、資産推移
- **リスク指標ダッシュボード**: 主要リスク指標の視覚化
- **取引分布**: 利益/損失の分布と統計
- **ヒートマップ**: パラメータ感度と最適化結果

## 使用方法

### 基本的なバックテスト評価
```python
from src.evaluation import evaluation
from src.evaluation.backtest import evaluate_strategies

# 戦略のバックテスト評価を実行
results = evaluate_strategies.backtest(
    strategy=my_strategy,
    data=historical_data,
    initial_capital=1000000,
    commission=0.001,
    slippage=0.0005,
    start_date='2020-01-01',
    end_date='2022-12-31'
)

# パフォーマンス指標を計算
performance = evaluation.calculate_metrics(
    results=results,
    risk_free_rate=0.02,
    metrics=['return', 'sharpe', 'sortino', 'max_drawdown', 'win_rate']
)

# 結果を表示
print(performance)
```

### 複数戦略の比較
```python
from src.evaluation.backtest import compare_strategies

# 複数の戦略を比較
comparison = compare_strategies.compare(
    strategies=[strategy1, strategy2, strategy3],
    data=historical_data,
    initial_capital=1000000,
    benchmark='SPY',  # ベンチマーク（S&P 500 ETF）
    metrics=['return', 'sharpe', 'sortino', 'max_drawdown', 'win_rate'],
    period='yearly'  # 年次パフォーマンス比較
)

# 比較結果を可視化
from src.evaluation.model import visualizer
visualizer.plot_comparison(comparison)
```

### リアルタイム評価
```python
from src.evaluation.realtime import evaluator

# リアルタイム評価器を初期化
live_evaluator = evaluator.RealtimeEvaluator(
    strategy=my_strategy,
    metrics=['return', 'sharpe', 'drawdown', 'win_rate'],
    alert_thresholds={
        'drawdown': -0.05,  # 5%以上のドローダウンでアラート
        'win_rate': 0.4     # 勝率が40%以下でアラート
    }
)

# 新しいデータポイントで評価を更新
live_evaluator.update(new_data_point)

# 現在のパフォーマンス状態を取得
current_performance = live_evaluator.get_current_performance()
```

### 高度なリスク分析
```python
from src.evaluation.model.metrics import risk

# バリューアットリスク（VaR）を計算
var_95 = risk.calculate_var(
    returns=strategy_returns,
    confidence_level=0.95,
    method='historical'
)

# 条件付きバリューアットリスク（CVaR/Expected Shortfall）を計算
cvar_95 = risk.calculate_cvar(
    returns=strategy_returns,
    confidence_level=0.95
)

# ストレステストを実行
stress_results = risk.stress_test(
    strategy=my_strategy,
    scenarios=[
        {'name': 'Market Crash', 'market_return': -0.20, 'volatility': 0.40},
        {'name': 'Rate Hike', 'interest_rate': 0.02, 'market_return': -0.05}
    ]
)
```

## 評価指標

### リターン指標
- **累積リターン**: 総合的なパフォーマンス
- **年率リターン**: 年率換算したパフォーマンス
- **月次/日次リターン**: 短期的なパフォーマンス
- **リターン分布**: リターンの統計的分布

### リスク指標
- **ボラティリティ**: リターンの標準偏差
- **シャープレシオ**: リスク調整済みリターン
- **ソルティノレシオ**: 下方リスク調整済みリターン
- **最大ドローダウン**: 最大の資産価値下落
- **VaR/CVaR**: バリューアットリスクと条件付きVaR
- **ベータ**: 市場に対する感応度

### 取引指標
- **勝率**: 利益が出た取引の割合
- **損益比**: 平均利益と平均損失の比率
- **期待値**: 1取引あたりの期待リターン
- **取引回数**: 期間中の取引頻度
- **平均保有期間**: ポジションの平均保有日数

## 設定
評価設定は `src/system/config.py` で管理されています。主な設定項目：
- バックテストパラメータ
- リスク計算パラメータ
- ベンチマーク設定
- レポート生成設定

## 依存関係
- pandas
- numpy
- scipy
- matplotlib
- seaborn
- pyfolio (オプション)

## 将来の拡張
- モンテカルロシミュレーション
- 機械学習ベースのパフォーマンス予測
- 高度なアトリビューション分析
- インタラクティブなウェブダッシュボード
- リアルタイムベンチマーキング