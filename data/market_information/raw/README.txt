# 生市場データディレクトリ

このディレクトリには、APIやデータプロバイダーから取得した未処理の生データが保存されます。

## ファイル形式
- CSV: 一般的な時系列データ
- JSON: API応答データ
- XLSX/XLS: エクセルデータ
- TXT: テキスト形式のデータ

## 命名規則
source_market_symbol_timeframe_YYYYMMDD.extension

例：
- yahoo_nasdaq_AAPL_daily_20200101.csv
- alphavantage_jpy_7203_hourly_20210101.json
- jpx_tosho_list_20220101.xlsx
- nasdaq_listed_20230101.txt

## データソース
- Yahoo Finance
- Alpha Vantage
- Japan Exchange Group (JPX)
- NASDAQ
- その他のデータプロバイダー

## 注意事項
- このディレクトリのデータは未処理であり、欠損値や異常値が含まれている可能性があります
- 処理前のデータの整合性を確認してください
- 大規模なデータファイルはGitで追跡されない場合があります（.gitignoreを確認）