# バックテスト結果ディレクトリ

このディレクトリには、戦略のバックテスト結果が保存されます。

## ファイル形式
- CSV: パフォーマンス指標の詳細データ
- JSON: 設定とメタデータ
- PNG/JPG: パフォーマンスグラフと可視化

## 命名規則
strategy_name_YYYYMMDD_parameters.extension

例：
- moving_average_20230101_fast10_slow30.csv
- rsi_20230215_period14_overbought70_oversold30.json
- ml_model_20230320_features5_depth3.png