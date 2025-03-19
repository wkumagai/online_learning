# 処理済み市場データディレクトリ

このディレクトリには、生データを処理・変換した後の市場データが保存されます。

## ファイル形式
- CSV: 処理済み時系列データ
- Parquet: 大規模データセット
- HDF5: 高次元データと複雑な構造

## 命名規則
market_symbol_timeframe_YYYYMMDD_YYYYMMDD.extension

例：
- nasdaq_AAPL_daily_20200101_20201231.csv
- jpy_7203_hourly_20210101_20210630.parquet
- forex_USDJPY_minute_20220101_20220131.h5

## 処理内容
- 欠損値の処理
- 異常値の検出と修正
- 特徴量エンジニアリング
- 正規化/標準化
- リサンプリング（日次、週次、月次など）