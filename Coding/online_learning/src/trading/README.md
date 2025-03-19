# 取引システム

実運用モードとペーパートレードモードを切り替え可能な取引システム

## 概要

このシステムは、テクニカル分析に基づく取引戦略を実行し、実際の取引またはシミュレーション取引を行うためのフレームワークを提供します。主な特徴は以下の通りです：

- 実運用モードとペーパートレードモードの切り替え
- 複数の取引戦略のサポート
- リスク管理機能
- パフォーマンス分析

## インストール

必要なパッケージをインストールします：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本的な使用方法

```bash
python trading/main.py --mode paper --symbols NVDA,AAPL,MSFT --strategy TripleMA
```

### コマンドラインオプション

- `--mode`: 実行モード（`paper`または`real`）
- `--capital`: 初期資金（デフォルト: 1,000,000円）
- `--risk`: 1トレードあたりのリスク（資金に対する割合、デフォルト: 0.02）
- `--max-position`: 最大ポジションサイズ（資金に対する割合、デフォルト: 0.1）
- `--symbols`: 対象銘柄（カンマ区切り、デフォルト: NVDA）
- `--strategy`: 使用する戦略（デフォルト: TripleMA）
- `--interval`: 更新間隔（秒、デフォルト: 60）

### 例

ペーパートレードモードでTeslaとAppleの株式を取引：

```bash
python trading/main.py --mode paper --symbols TSLA,AAPL --strategy MACD --interval 300
```

実運用モードでNVIDIAの株式を取引：

```bash
python trading/main.py --mode real --symbols NVDA --strategy RSIWithTrend --capital 2000000
```

## 利用可能な戦略

### 移動平均戦略

- `SimpleMA`: 単純移動平均戦略
  - 短期移動平均が長期移動平均を上回ったら買い
  - 短期移動平均が長期移動平均を下回ったら売り

- `TripleMA`: 三重移動平均戦略
  - 短期>中期>長期の場合は強い買いシグナル
  - 短期<中期<長期の場合は強い売りシグナル

### RSI戦略

- `RSI`: RSI（相対力指数）戦略
  - RSIが下限値を下回ったら買い
  - RSIが上限値を上回ったら売り

- `RSIWithTrend`: トレンド確認付きRSI戦略
  - 上昇トレンドでRSIが下限値を下回ったら買い
  - 下降トレンドでRSIが上限値を上回ったら売り

### MACD戦略

- `MACD`: MACD（移動平均収束拡散）戦略
  - MACDがシグナルラインを上抜けたら買い
  - MACDがシグナルラインを下抜けたら売り

- `MACDHistogram`: MACDヒストグラム戦略
  - ヒストグラムが負から正に変化したら買い
  - ヒストグラムが正から負に変化したら売り

- `MACDDivergence`: MACDダイバージェンス戦略
  - 価格が下降しているのにMACDが上昇している場合は買い（ポジティブダイバージェンス）
  - 価格が上昇しているのにMACDが下降している場合は売り（ネガティブダイバージェンス）

## カスタム戦略の追加

新しい戦略を追加するには、`trading/common/strategies/`ディレクトリに新しいPythonファイルを作成し、`Strategy`クラスを継承した戦略クラスを実装します。

```python
from trading.common.strategy_manager import Strategy

class MyCustomStrategy(Strategy):
    def __init__(self, params=None):
        default_params = {
            'param1': 10,
            'param2': 20
        }
        
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
    
    def calculate_indicators(self, data):
        # テクニカル指標の計算
        df = data.copy()
        # ...
        return df
    
    def generate_signals(self, data):
        # シグナルの生成
        df = self.calculate_indicators(data)
        # ...
        return signals
```

その後、`main.py`で新しい戦略を登録します：

```python
strategy_manager.register_strategy('MyCustom', MyCustomStrategy())
```

## ログとレポート

取引システムは以下のログとレポートを生成します：

- 取引ログ: `logs/trading_YYYYMMDD_HHMMSS.log`
- 取引履歴: `logs/paper_trade_history_YYYYMMDD.json`（ペーパートレードモード）
- パフォーマンス指標: `logs/paper_performance_metrics_YYYYMMDD.json`（ペーパートレードモード）
- 最終レポート: `logs/paper_final_report_YYYYMMDD_HHMMSS.json`（ペーパートレードモード）

## ライセンス

MIT
