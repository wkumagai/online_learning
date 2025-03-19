import pandas as pd
import yfinance as yf
import time
import csv
import os
import datetime
import argparse
from tqdm import tqdm
import random
import math

def read_nasdaqlisted_file(file_path='data/nasdaqlisted.txt'):
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

def fetch_historical_data(ticker, start_date, end_date, retry_count=3, initial_retry_delay=60, max_retry_delay=600):
    """
    ティッカーの過去の株価データを取得する
    
    Parameters:
    -----------
    ticker : str
        取得するティッカーシンボル
    start_date : str
        開始日（YYYY-MM-DD形式）
    end_date : str
        終了日（YYYY-MM-DD形式）
    retry_count : int
        レート制限エラーが発生した場合の再試行回数
    initial_retry_delay : int
        初回再試行までの待機時間（秒）
    max_retry_delay : int
        最大再試行待機時間（秒）
    
    Returns:
    --------
    tuple
        (成功したかどうか, データまたはエラーメッセージ)
    """
    current_retry_delay = initial_retry_delay
    
    for attempt in range(retry_count + 1):
        try:
            # yfinanceでティッカーを取得
            stock = yf.Ticker(ticker)
            
            # 過去の株価データを取得
            hist_data = stock.history(start=start_date, end=end_date)
            
            # データが空かどうかを確認
            if hist_data.empty:
                return False, f"データが空です"
            
            # データが取得できた場合
            return True, hist_data
                
        except Exception as e:
            error_msg = str(e)
            
            # レート制限エラーかどうかを確認
            if ("Too Many Requests" in error_msg or "rate limit" in error_msg.lower()) and attempt < retry_count:
                # 再試行前に待機（指数バックオフ）
                print(f"  レート制限エラー。{current_retry_delay}秒後に再試行します（{attempt+1}/{retry_count}）...")
                time.sleep(current_retry_delay)
                
                # 次回の待機時間を増やす（最大値まで）
                current_retry_delay = min(current_retry_delay * 2, max_retry_delay)
                continue
            
            # 再試行回数を超えたか、他のエラーの場合
            return False, f"エラー: {error_msg}"

def save_data_to_csv(ticker, data, output_dir='data/historical_data'):
    """
    取得したデータをCSVファイルに保存する
    
    Parameters:
    -----------
    ticker : str
        ティッカーシンボル
    data : pandas.DataFrame
        保存するデータ
    output_dir : str
        出力ディレクトリ
    
    Returns:
    --------
    bool
        保存に成功したかどうか
    """
    try:
        # 出力ディレクトリが存在しない場合は作成
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # ファイルパスを作成
        file_path = os.path.join(output_dir, f"{ticker}.csv")
        
        # CSVに保存
        data.to_csv(file_path)
        
        return True
    except Exception as e:
        print(f"  データの保存中にエラーが発生しました: {e}")
        return False

def update_progress_log(results, log_file='data/historical_data_progress.csv'):
    """
    進捗状況をCSVファイルに保存する
    
    Parameters:
    -----------
    results : list
        処理結果のリスト
    log_file : str
        ログファイルのパス
    """
    try:
        # DataFrameに変換
        df = pd.DataFrame(results)
        
        # CSVに保存
        df.to_csv(log_file, index=False)
        
        print(f"進捗状況を {log_file} に保存しました（{len(results)} 件）")
    except Exception as e:
        print(f"進捗状況の保存中にエラーが発生しました: {e}")

def estimate_remaining_time(processed, total, elapsed_time):
    """
    残り時間を推定する
    
    Parameters:
    -----------
    processed : int
        処理済みの数
    total : int
        全体の数
    elapsed_time : float
        経過時間（秒）
    
    Returns:
    --------
    tuple
        (残り時間（秒）, 完了予想時刻)
    """
    if processed == 0:
        return None, None
    
    # 1件あたりの平均処理時間
    avg_time_per_item = elapsed_time / processed
    
    # 残りの件数
    remaining_items = total - processed
    
    # 残り時間の推定
    remaining_time = avg_time_per_item * remaining_items
    
    # 完了予想時刻
    completion_time = datetime.datetime.now() + datetime.timedelta(seconds=remaining_time)
    
    return remaining_time, completion_time

def format_time(seconds):
    """
    秒数を時間:分:秒の形式にフォーマットする
    
    Parameters:
    -----------
    seconds : float
        フォーマットする秒数
    
    Returns:
    --------
    str
        フォーマットされた時間
    """
    if seconds is None:
        return "不明"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    return f"{hours}時間 {minutes}分 {secs}秒"

def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='NASDAQ上場銘柄の過去10年間の株価データを取得')
    parser.add_argument('--input', type=str, default='data/nasdaqlisted.txt', help='入力ファイルのパス')
    parser.add_argument('--output-dir', type=str, default='data/historical_data', help='出力ディレクトリ')
    parser.add_argument('--years', type=int, default=10, help='取得する年数')
    parser.add_argument('--delay', type=float, default=1.0, help='リクエスト間の待機時間（秒）')
    parser.add_argument('--retry-delay', type=int, default=60, help='レート制限時の初期待機時間（秒）')
    parser.add_argument('--max-retry-delay', type=int, default=600, help='レート制限時の最大待機時間（秒）')
    parser.add_argument('--retry-count', type=int, default=3, help='レート制限時の再試行回数')
    parser.add_argument('--resume', action='store_true', help='前回の続きから処理を再開する')
    parser.add_argument('--shuffle', action='store_true', help='ティッカーリストをシャッフルする')
    parser.add_argument('--limit', type=int, default=0, help='処理する銘柄数の上限（0の場合は全て）')
    args = parser.parse_args()
    
    print("NASDAQ上場銘柄の過去株価データ取得")
    print("================================")
    
    # 開始日と終了日を計算
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=365 * args.years)).strftime('%Y-%m-%d')
    
    print(f"期間: {start_date} から {end_date} まで（約{args.years}年間）")
    print(f"リクエスト間の待機時間: {args.delay}秒")
    print(f"レート制限時の初期待機時間: {args.retry_delay}秒")
    print(f"レート制限時の最大待機時間: {args.max_retry_delay}秒")
    print(f"レート制限時の再試行回数: {args.retry_count}回")
    
    # nasdaqlisted.txtからティッカーを読み込む
    tickers = read_nasdaqlisted_file(args.input)
    
    if not tickers:
        print("ティッカーを読み込めませんでした。終了します。")
        return
    
    # ティッカーリストをシャッフル（オプション）
    if args.shuffle:
        print("ティッカーリストをシャッフルしています...")
        random.shuffle(tickers)
    
    # 前回の進捗状況を読み込む（オプション）
    processed_tickers = set()
    results = []
    
    if args.resume and os.path.exists('data/historical_data_progress.csv'):
        try:
            print("前回の進捗状況を読み込んでいます...")
            progress_df = pd.read_csv('data/historical_data_progress.csv')
            
            # 処理済みのティッカーを取得
            processed_tickers = set(progress_df['Ticker'].tolist())
            
            # 結果リストを初期化
            results = progress_df.to_dict('records')
            
            print(f"前回の進捗状況を読み込みました。{len(processed_tickers)}銘柄が既に処理済みです。")
        except Exception as e:
            print(f"前回の進捗状況の読み込み中にエラーが発生しました: {e}")
            processed_tickers = set()
            results = []
    
    # 処理するティッカーをフィルタリング
    tickers_to_process = [t for t in tickers if t not in processed_tickers]
    
    # 処理する銘柄数を制限（オプション）
    if args.limit > 0 and args.limit < len(tickers_to_process):
        print(f"処理する銘柄数を {args.limit} に制限します。")
        tickers_to_process = tickers_to_process[:args.limit]
    
    print(f"\n{len(tickers_to_process)}銘柄の株価データを取得します...")
    
    # 出力ディレクトリが存在しない場合は作成
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"出力ディレクトリ {args.output_dir} を作成しました。")
    
    # 開始時間を記録
    start_time = time.time()
    rate_limit_count = 0
    consecutive_rate_limits = 0
    current_delay = args.delay
    
    # 各ティッカーを処理
    for i, ticker in enumerate(tickers_to_process):
        # 経過時間を計算
        elapsed_time = time.time() - start_time
        
        # 残り時間を推定
        remaining_time, completion_time = estimate_remaining_time(i, len(tickers_to_process), elapsed_time)
        
        # 進捗状況を表示
        completion_str = f"完了予想時刻: {completion_time.strftime('%Y-%m-%d %H:%M:%S')}" if completion_time else "完了予想時刻: 不明"
        print(f"\n[{i+1}/{len(tickers_to_process)}] {ticker} の株価データを取得中... (経過時間: {format_time(elapsed_time)}, 残り時間: {format_time(remaining_time)}, {completion_str})")
        
        # 株価データを取得
        success, data = fetch_historical_data(
            ticker, 
            start_date, 
            end_date, 
            retry_count=args.retry_count,
            initial_retry_delay=args.retry_delay,
            max_retry_delay=args.max_retry_delay
        )
        
        # 結果を記録
        result = {
            'Ticker': ticker,
            'Success': success,
            'Timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if success:
            # データを保存
            save_success = save_data_to_csv(ticker, data, args.output_dir)
            
            # 結果を表示
            print(f"  成功: {ticker} の株価データを取得しました（{len(data)}行）")
            
            # レート制限カウンターをリセット
            consecutive_rate_limits = 0
            
            # 待機時間を元に戻す（レート制限が続いた後）
            if current_delay > args.delay:
                current_delay = args.delay
                print(f"  レート制限が解消されました。待機時間を{current_delay}秒に戻します。")
            
            # 結果に詳細を追加
            result['Rows'] = len(data)
            result['SaveSuccess'] = save_success
            result['Message'] = "成功"
        else:
            # エラーメッセージを表示
            error_msg = data if isinstance(data, str) else "不明なエラー"
            print(f"  失敗: {ticker} の株価データを取得できませんでした。理由: {error_msg}")
            
            # レート制限エラーかどうかを確認
            if "Too Many Requests" in error_msg or "rate limit" in error_msg.lower():
                rate_limit_count += 1
                consecutive_rate_limits += 1
                
                # 連続したレート制限エラーが発生した場合、待機時間を増やす
                if consecutive_rate_limits >= 3:
                    old_delay = current_delay
                    current_delay = min(current_delay * 1.5, 10.0)  # 最大10秒まで
                    print(f"  連続したレート制限エラーが発生しています。待機時間を{old_delay}秒から{current_delay}秒に増やします。")
            else:
                consecutive_rate_limits = 0
            
            # 結果にエラーメッセージを追加
            result['Message'] = error_msg
        
        # 結果リストに追加
        results.append(result)
        
        # 10銘柄ごとに進捗状況を保存
        if (i + 1) % 10 == 0 or (i + 1) == len(tickers_to_process):
            update_progress_log(results)
        
        # レート制限を避けるために待機
        if i < len(tickers_to_process) - 1:  # 最後の銘柄でなければ待機
            time.sleep(current_delay)
    
    # 終了時間を記録
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 成功率を計算
    success_count = sum(1 for r in results if r.get('Success', False))
    success_rate = (success_count / len(results)) * 100 if results else 0
    
    # レート制限の発生率を計算
    rate_limit_rate = (rate_limit_count / len(results)) * 100 if results else 0
    
    print("\n処理が完了しました。")
    print(f"処理時間: {format_time(elapsed_time)}")
    print(f"処理した銘柄数: {len(results)}")
    print(f"成功した銘柄数: {success_count} ({success_rate:.2f}%)")
    print(f"失敗した銘柄数: {len(results) - success_count} ({100 - success_rate:.2f}%)")
    print(f"レート制限エラーの発生数: {rate_limit_count} ({rate_limit_rate:.2f}%)")
    print(f"\n結果は {args.output_dir} ディレクトリに保存されました。")
    print(f"進捗状況は data/historical_data_progress.csv に保存されました。")

if __name__ == "__main__":
    main()