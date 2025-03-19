"""
stock_data_utils.py

株価データの読み込みと前処理のためのユーティリティ関数
"""

import pandas as pd
import numpy as np
import os
import glob
import matplotlib.pyplot as plt
from typing import Tuple, Optional, Dict, List, Union

def find_stock_data(symbol: str, data_dir: str = 'data') -> Optional[str]:
    """
    指定された銘柄のCSVファイルを探す
    
    Parameters:
    -----------
    symbol : str
        銘柄シンボル（例: 'TSLA'）
    data_dir : str
        データディレクトリのパス
        
    Returns:
    --------
    str or None
        見つかったCSVファイルのパス、見つからない場合はNone
    """
    # 可能性のあるパスを探索
    possible_paths = [
        os.path.join(data_dir, 'historical_data_US', f'{symbol}.csv'),
        os.path.join(data_dir, 'historical_data_JP', f'{symbol}.csv'),
        os.path.join(data_dir, f'{symbol}.csv')
    ]
    
    # 再帰的に検索
    for pattern in [f'**/{symbol}.csv', f'**/{symbol}_*.csv']:
        found_files = glob.glob(os.path.join(data_dir, pattern), recursive=True)
        possible_paths.extend(found_files)
    
    # 見つかったパスを返す
    for path in possible_paths:
        if os.path.exists(path):
            print(f"銘柄 {symbol} のデータファイルが見つかりました: {path}")
            return path
    
    print(f"銘柄 {symbol} のデータファイルが見つかりませんでした。")
    
    # 代替として、historical_data_USディレクトリ内の最初のCSVファイルを使用
    us_data_dir = os.path.join(data_dir, 'historical_data_US')
    if os.path.exists(us_data_dir):
        csv_files = glob.glob(os.path.join(us_data_dir, '*.csv'))
        if csv_files:
            print(f"代替として {csv_files[0]} を使用します。")
            return csv_files[0]
    
    return None

def load_stock_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    株価データをロードする
    
    Parameters:
    -----------
    file_path : str
        CSVファイルのパス
        
    Returns:
    --------
    pandas.DataFrame or None
        ロードされた株価データ、エラーの場合はNone
    """
    try:
        # CSVファイルを読み込む
        df = pd.read_csv(file_path, index_col=0, parse_dates=True)
        
        # カラム名を小文字に変換
        df.columns = [col.lower() for col in df.columns]
        
        # 必要なカラムが存在するか確認
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            # 一般的な代替カラム名をマッピング
            column_mapping = {
                'open': ['始値', 'オープン', 'open price'],
                'high': ['高値', 'ハイ', 'high price'],
                'low': ['安値', 'ロー', 'low price'],
                'close': ['終値', 'クローズ', 'close price', 'adj close', 'adjusted close'],
                'volume': ['出来高', 'ボリューム', 'trading volume']
            }
            
            # 代替カラム名を試す
            for missing_col in missing_columns:
                for alt_name in column_mapping[missing_col]:
                    if alt_name in df.columns:
                        df[missing_col] = df[alt_name]
                        break
            
            # 再度確認
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"警告: 以下の必須カラムがデータに存在しません: {missing_columns}")
                return None
        
        print(f"データを正常にロードしました。行数: {len(df)}, 期間: {df.index[0]} から {df.index[-1]}")
        return df
        
    except Exception as e:
        print(f"データのロード中にエラーが発生しました: {str(e)}")
        return None

def split_data(df: pd.DataFrame, train_size: float = 0.6, val_size: float = 0.2, test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    データを訓練、検証、テストセットに分割する
    
    Parameters:
    -----------
    df : pandas.DataFrame
        分割する株価データ
    train_size : float
        訓練データの割合
    val_size : float
        検証データの割合
    test_size : float
        テストデータの割合
        
    Returns:
    --------
    tuple
        (訓練データ, 検証データ, テストデータ)
    """
    # 合計が1になることを確認
    total = train_size + val_size + test_size
    if total != 1.0:
        print(f"警告: 分割比率の合計が1.0ではありません ({total})。正規化します。")
        train_size /= total
        val_size /= total
        test_size /= total
    
    # 時系列データの場合は時間順に分割
    data_length = len(df)
    train_end = int(data_length * train_size)
    val_end = train_end + int(data_length * val_size)
    
    train_data = df.iloc[:train_end]
    val_data = df.iloc[train_end:val_end]
    test_data = df.iloc[val_end:]
    
    print(f"データを分割しました:")
    print(f"  訓練データ: {len(train_data)} 行 ({train_size*100:.1f}%), 期間: {train_data.index[0]} から {train_data.index[-1]}")
    print(f"  検証データ: {len(val_data)} 行 ({val_size*100:.1f}%), 期間: {val_data.index[0]} から {val_data.index[-1]}")
    print(f"  テストデータ: {len(test_data)} 行 ({test_size*100:.1f}%), 期間: {test_data.index[0]} から {test_data.index[-1]}")
    
    return train_data, val_data, test_data

def preprocess_stock_data(df: pd.DataFrame, fill_missing: bool = True, normalize: bool = False) -> pd.DataFrame:
    """
    株価データの前処理を行う
    
    Parameters:
    -----------
    df : pandas.DataFrame
        前処理する株価データ
    fill_missing : bool
        欠損値を補完するかどうか
    normalize : bool
        データを正規化するかどうか
        
    Returns:
    --------
    pandas.DataFrame
        前処理された株価データ
    """
    # データのコピーを作成
    processed_df = df.copy()
    
    # カラム名を小文字に変換
    processed_df.columns = [col.lower() for col in processed_df.columns]
    
    # 欠損値の補完
    if fill_missing:
        # 前方補完
        processed_df = processed_df.fillna(method='ffill')
        # 後方補完（前方補完で埋められなかった場合）
        processed_df = processed_df.fillna(method='bfill')
    
    # 正規化
    if normalize:
        # 各カラムを0-1の範囲に正規化
        for col in ['open', 'high', 'low', 'close']:
            if col in processed_df.columns:
                min_val = processed_df[col].min()
                max_val = processed_df[col].max()
                processed_df[f'{col}_norm'] = (processed_df[col] - min_val) / (max_val - min_val)
    
    return processed_df

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    テクニカル指標を計算する
    
    Parameters:
    -----------
    df : pandas.DataFrame
        株価データ
        
    Returns:
    --------
    pandas.DataFrame
        テクニカル指標が追加された株価データ
    """
    # データのコピーを作成
    tech_df = df.copy()
    
    # カラム名を小文字に変換
    tech_df.columns = [col.lower() for col in tech_df.columns]
    
    # 移動平均
    for window in [5, 10, 20, 50, 200]:
        tech_df[f'ma_{window}'] = tech_df['close'].rolling(window=window).mean()
    
    # ボリンジャーバンド（20日移動平均±2標準偏差）
    ma_20 = tech_df['close'].rolling(window=20).mean()
    std_20 = tech_df['close'].rolling(window=20).std()
    tech_df['bb_upper'] = ma_20 + 2 * std_20
    tech_df['bb_lower'] = ma_20 - 2 * std_20
    
    # RSI（14日）
    delta = tech_df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    tech_df['rsi_14'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema_12 = tech_df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = tech_df['close'].ewm(span=26, adjust=False).mean()
    tech_df['macd'] = ema_12 - ema_26
    tech_df['macd_signal'] = tech_df['macd'].ewm(span=9, adjust=False).mean()
    tech_df['macd_hist'] = tech_df['macd'] - tech_df['macd_signal']
    
    return tech_df

def plot_stock_data(df: pd.DataFrame, title: str = 'Stock Price', save_path: Optional[str] = None):
    """
    株価データをプロットする
    
    Parameters:
    -----------
    df : pandas.DataFrame
        プロットする株価データ
    title : str
        グラフのタイトル
    save_path : str or None
        保存先のパス、Noneの場合は保存しない
    """
    # カラム名を小文字に変換
    plot_df = df.copy()
    plot_df.columns = [col.lower() for col in plot_df.columns]
    
    # プロット
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
    
    # 株価チャート
    axes[0].plot(plot_df.index, plot_df['close'], label='Close')
    
    # 移動平均線
    for ma in [col for col in plot_df.columns if col.startswith('ma_')]:
        axes[0].plot(plot_df.index, plot_df[ma], label=ma.upper())
    
    # ボリンジャーバンド
    if 'bb_upper' in plot_df.columns and 'bb_lower' in plot_df.columns:
        axes[0].plot(plot_df.index, plot_df['bb_upper'], 'r--', label='BB Upper')
        axes[0].plot(plot_df.index, plot_df['bb_lower'], 'g--', label='BB Lower')
    
    axes[0].set_title(title)
    axes[0].set_ylabel('Price')
    axes[0].legend()
    axes[0].grid(True)
    
    # 出来高
    axes[1].bar(plot_df.index, plot_df['volume'])
    axes[1].set_ylabel('Volume')
    axes[1].grid(True)
    
    plt.tight_layout()
    
    # 保存
    if save_path:
        plt.savefig(save_path)
        print(f"チャートを {save_path} に保存しました。")
    
    plt.show()