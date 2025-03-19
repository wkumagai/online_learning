import pandas as pd
import yfinance as yf
import time
import csv
import os
import argparse
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

def read_nasdaqlisted_file(file_path='nasdaqlisted.txt'):
    """
    nasdaqlisted.txtファイルからティッカーシンボルを読み込む
    
    Parameters:
    -----------
    file_path : str
        nasdaqlisted.txtファイルのパス
    
    Returns:
    --------
    list
        ティッカーシンボルのリスト
    """
    print(f"{file_path}からティッカーシンボルを読み込んでいます...")
    
    tickers = []
    
    try:
        # ファイルを開いて読み込む
        with open(file_path, 'r') as f:
            # CSVリーダーを使用してパイプ区切りのファイルを読み込む
            reader = csv.reader(f, delimiter='|')
            # ヘッダー行をスキップ
            next(reader)
            
            # 各行からティッカーシンボルを取得
            for row in reader:
                if len(row) > 0:
                    ticker = row[0].strip()
                    if ticker:  # 空でないことを確認
                        tickers.append(ticker)
        
        print(f"合計 {len(tickers)} 個のティッカーシンボルを読み込みました。")
        return tickers
    
    except Exception as e:
        print(f"ファイルの読み込み中にエラーが発生しました: {e}")
        return []

def check_ticker_availability(ticker, retry_count=3, retry_delay=5):
    """
    ティッカーがyfinanceで利用可能かどうかを確認する
    
    Parameters:
    -----------
    ticker : str
        確認するティッカーシンボル
    retry_count : int
        レート制限エラーが発生した場合の再試行回数
    retry_delay : int
        再試行までの待機時間（秒）
    
    Returns:
    --------
    dict
        ティッカーと利用可能性を含む辞書
    """
    for attempt in range(retry_count + 1):
        try:
            # yfinanceでティッカーを取得
            stock = yf.Ticker(ticker)
            
            # 基本情報を取得してみる
            info = stock.info
            
            # 有効なデータが取得できたかを確認
            is_available = 'symbol' in info and info['symbol'] == ticker
            
            return {
                'Symbol': ticker,
                'Available': is_available
            }
                
        except Exception as e:
            error_msg = str(e)
            
            # レート制限エラーかどうかを確認
            if "Too Many Requests" in error_msg and attempt < retry_count:
                # 再試行前に待機
                print(f"  レート制限エラー。{retry_delay}秒後に再試行します（{attempt+1}/{retry_count}）...")
                time.sleep(retry_delay)
                continue
            
            # 再試行回数を超えたか、他のエラーの場合
            return {
                'Symbol': ticker,
                'Available': False,
                'Error': error_msg[:100]  # エラーメッセージを短く切り詰める
            }

def process_batch(tickers, batch_size=20, sleep_between_batches=30, sleep_between_requests=1):
    """
    ティッカーをバッチ処理して、レート制限を回避する
    
    Parameters:
    -----------
    tickers : list
        処理するティッカーのリスト
    batch_size : int
        一度に処理するティッカーの数
    sleep_between_batches : int
        バッチ間の待機時間（秒）
    sleep_between_requests : int
        リクエスト間の待機時間（秒）
    
    Returns:
    --------
    list
        各ティッカーの結果を含むリスト
    """
    results = []
    total = len(tickers)
    processed = 0
    
    # バッチに分割
    for i in range(0, total, batch_size):
        batch = tickers[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size
        
        print(f"\nバッチ {batch_num}/{total_batches} を処理中（{len(batch)} 銘柄）...")
        
        # バッチ内の各ティッカーを処理
        for j, ticker in enumerate(batch):
            try:
                print(f"  [{processed+1}/{total}] {ticker} をチェック中...", end="", flush=True)
                
                # ティッカーの利用可能性をチェック
                result = check_ticker_availability(ticker)
                
                # 結果を表示
                status = "利用可能" if result.get('Available', False) else f"利用不可 ({result.get('Error', 'Unknown error')})"
                print(f" {status}")
                
                # 結果をリストに追加
                results.append(result)
                
                # 進捗状況を更新
                processed += 1
                
                # レート制限を避けるために待機
                if j < len(batch) - 1:  # バッチの最後のアイテムでなければ待機
                    time.sleep(sleep_between_requests)
                
            except Exception as e:
                print(f" エラー: {str(e)[:100]}")
                results.append({
                    'Symbol': ticker,
                    'Available': False,
                    'Error': f"処理エラー: {str(e)[:100]}"
                })
                processed += 1
        
        # 中間結果を保存
        save_results(results, 'data/nasdaq_ticker_availability_intermediate.csv')
        
        # バッチ間の待機（最後のバッチでなければ）
        if i + batch_size < total:
            print(f"レート制限を回避するために {sleep_between_batches} 秒待機しています...")
            time.sleep(sleep_between_batches)
    
    return results

def save_results(results, filename):
    """
    結果をCSVファイルに保存する
    
    Parameters:
    -----------
    results : list
        保存する結果のリスト
    filename : str
        保存先のファイル名
    """
    try:
        # DataFrameに変換
        df = pd.DataFrame(results)
        
        # CSVに保存
        df.to_csv(filename, index=False)
        print(f"結果を {filename} に保存しました（{len(results)} 件）")
    except Exception as e:
        print(f"結果の保存中にエラーが発生しました: {e}")

def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='NASDAQリストティッカーのyfinance利用可能性チェック')
    parser.add_argument('--sample', type=int, default=0, help='チェックするランダムサンプルのサイズ（0の場合は全て）')
    parser.add_argument('--batch-size', type=int, default=20, help='一度に処理するバッチサイズ')
    parser.add_argument('--batch-delay', type=int, default=30, help='バッチ間の待機時間（秒）')
    parser.add_argument('--request-delay', type=int, default=1, help='リクエスト間の待機時間（秒）')
    parser.add_argument('--input', type=str, default='nasdaqlisted.txt', help='入力ファイルのパス')
    parser.add_argument('--output', type=str, default='data/nasdaq_ticker_availability_results.csv', help='出力ファイルのパス')
    args = parser.parse_args()
    
    print("NASDAQリストティッカーのyfinance利用可能性チェック")
    print("================================================")
    print(f"バッチサイズ: {args.batch_size}")
    print(f"バッチ間待機時間: {args.batch_delay}秒")
    print(f"リクエスト間待機時間: {args.request_delay}秒")
    
    # nasdaqlisted.txtからティッカーを読み込む
    tickers = read_nasdaqlisted_file(args.input)
    
    if not tickers:
        print("ティッカーを読み込めませんでした。終了します。")
        return
    
    # サンプリングが指定されている場合
    if args.sample > 0 and args.sample < len(tickers):
        print(f"{args.sample} 銘柄のランダムサンプルを選択しています...")
        tickers = random.sample(tickers, args.sample)
        print(f"サンプルサイズ: {len(tickers)} 銘柄")
    
    # バッチ処理でティッカーをチェック
    start_time = time.time()
    results = process_batch(
        tickers, 
        batch_size=args.batch_size, 
        sleep_between_batches=args.batch_delay,
        sleep_between_requests=args.request_delay
    )
    end_time = time.time()
    
    # 結果をDataFrameに変換
    results_df = pd.DataFrame(results)
    
    # 利用可能な銘柄と利用不可能な銘柄の数を計算
    available_count = results_df['Available'].sum()
    unavailable_count = len(results_df) - available_count
    
    # 利用可能率を計算
    availability_rate = (available_count / len(results_df)) * 100
    
    # 結果をCSVファイルに保存
    results_df.to_csv(args.output, index=False)
    
    # 処理時間を計算
    elapsed_time = end_time - start_time
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    
    print("\n結果:")
    print(f"チェックした銘柄数: {len(results_df)}")
    print(f"利用可能な銘柄数: {available_count} ({availability_rate:.2f}%)")
    print(f"利用不可能な銘柄数: {unavailable_count} ({100-availability_rate:.2f}%)")
    print(f"処理時間: {hours}時間 {minutes}分 {seconds}秒")
    print(f"\n結果は {args.output} に保存されました。")

if __name__ == "__main__":
    main()