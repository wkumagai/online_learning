# 市場情報モジュール

## 概要
市場情報モジュールは、様々なソースから金融市場データを収集、処理、保存するためのコンポーネントです。このモジュールは、取引戦略の開発と評価に必要な高品質なデータを提供します。

## 主要機能

### 1. データ収集
- **株式市場データ**: 日本、米国、その他の主要市場の株価データ
- **経済指標**: GDP、インフレ率、失業率などのマクロ経済データ
- **企業財務データ**: 決算情報、財務諸表、企業イベント
- **ニュースと感情データ**: 市場関連ニュース、ソーシャルメディア感情分析

### 2. データ処理
- **クリーニング**: 欠損値処理、異常値検出と修正
- **正規化**: 様々な時間枠と市場間でのデータ標準化
- **特徴量エンジニアリング**: テクニカル指標の計算、派生特徴量の作成
- **データ変換**: 様々な分析手法に適したフォーマットへの変換

### 3. データ保存
- **効率的なストレージ**: 最適なデータ形式と圧縮
- **バージョン管理**: データセットの変更追跡
- **メタデータ**: データソース、タイムスタンプ、品質指標の記録
- **アクセス制御**: 機密データの保護

## データソース
- Yahoo Finance
- Alpha Vantage
- Japan Exchange Group (JPX)
- NASDAQ
- Bloomberg (将来的に)
- Reuters (将来的に)

## 使用方法

### 基本的な使用例
```python
from src.market_information import market_information

# 日本株のデータを取得
japan_data = market_information.get_stock_data(
    market="japan",
    symbols=["7203.T", "9984.T"],  # トヨタ、ソフトバンク
    start_date="2022-01-01",
    end_date="2022-12-31",
    timeframe="daily"
)

# テクニカル指標を計算
processed_data = market_information.calculate_indicators(
    data=japan_data,
    indicators=["SMA", "RSI", "MACD"],
    parameters={"SMA": [20, 50, 200]}
)

# データを保存
market_information.save_data(
    data=processed_data,
    path="data/market_information/processed/japan_stocks_2022.csv"
)
```

### 高度な使用例
```python
# カスタムデータパイプラインの作成
pipeline = market_information.create_pipeline([
    {"function": "fetch_data", "params": {...}},
    {"function": "clean_data", "params": {...}},
    {"function": "calculate_indicators", "params": {...}},
    {"function": "save_data", "params": {...}}
])

# パイプラインを実行
pipeline.execute()

# スケジュールされたデータ更新を設定
market_information.schedule_update(
    pipeline=pipeline,
    schedule="daily",
    time="18:00",
    timezone="Asia/Tokyo"
)
```

## 設定
設定は `src/system/config.py` で管理されています。主な設定項目：
- API キーと認証情報
- データソースの優先順位
- キャッシュと保存設定
- 更新スケジュール

## 依存関係
- pandas
- numpy
- requests
- yfinance
- pandas-datareader
- ta-lib (テクニカル指標)
- beautifulsoup4 (ウェブスクレイピング)

## 将来の拡張
- リアルタイムデータストリーミング
- 代替データソースの統合
- 分散データ処理
- 高度なデータ品質モニタリング