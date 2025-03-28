# 戦略ログディレクトリ

このディレクトリには、戦略の実行ログとデバッグ情報が保存されます。

## ファイル形式
- LOG: テキスト形式のログファイル
- CSV: 構造化されたログデータ
- JSON: 詳細なログとメタデータ

## 命名規則
strategy_name_YYYYMMDD_HHMMSS.extension

例：
- moving_average_20230101_120000.log
- rsi_strategy_20230215_143000.csv
- ml_model_debug_20230320_093000.json

## ログ内容
- 戦略初期化パラメータ
- 実行時間とパフォーマンス指標
- 予測と実際の結果
- エラーと警告メッセージ
- デバッグ情報

## ログレベル
- INFO: 一般的な情報
- WARNING: 警告（データ品質の問題など）
- ERROR: エラー（実行失敗など）
- DEBUG: デバッグ情報（詳細な内部状態）

## 保持ポリシー
- 通常のログ: 30日間
- エラーログ: 90日間
- 重要な実行ログ: 永続的に保存

## 注意事項
- 機密情報（APIキーなど）はログに記録しないでください
- 大規模なログファイルは定期的にアーカイブまたは削除してください