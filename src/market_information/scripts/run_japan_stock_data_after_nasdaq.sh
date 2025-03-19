#!/bin/bash

# NASDAQ銘柄の処理が完了するのを待ってから、日本株の株価データを取得するスクリプト

# ログファイルのパス
LOG_FILE="data/run_japan_stock_data.log"

# 開始メッセージ
echo "$(date): NASDAQ銘柄の処理が完了するのを待っています..." | tee -a $LOG_FILE

# NASDAQ銘柄の処理が完了するまで待機
while ps aux | grep -v grep | grep "fetch_nasdaq_historical_data.py" > /dev/null; do
    echo "$(date): NASDAQ銘柄の処理が実行中です。1分後に再確認します..." | tee -a $LOG_FILE
    sleep 60
done

# NASDAQ銘柄の処理が完了したら、日本株の株価データを取得
echo "$(date): NASDAQ銘柄の処理が完了しました。日本株の株価データの取得を開始します..." | tee -a $LOG_FILE

# 日本株の株価データを取得
python data/fetch_japan_stock_data.py --delay 2 --retry-delay 60 --max-retry-delay 300 --retry-count 3 | tee -a $LOG_FILE

# 完了メッセージ
echo "$(date): 日本株の株価データの取得が完了しました。" | tee -a $LOG_FILE