"""
evaluate_strategies.py

任意の銘柄に対して複数の取引戦略を評価するスクリプト
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import argparse
from typing import Dict, List, Tuple, Optional, Union
from strategies.evaluation.stock_data_utils import load_stock_data, split_data

# strategiesモジュールをインポート
sys.path.append('.')
from strategies.Technical.moving_average import SimpleMAStrategy, TripleMAStrategy
from strategies.Technical.momentum import RSIStrategy, MACDStrategy

def evaluate_strategy(strategy, data: pd.DataFrame, name: str, initial_capital: float = 10000) -> Dict:
    """
    戦略の性能を評価する
    
    Parameters:
    -----------
    strategy : BaseStrategy
        評価する戦略
    data : pandas.DataFrame
        評価用データ
    name : str
        データセット名（訓練/検証/テスト）
    initial_capital : float
        初期資金
        
    Returns:
    --------
    dict
        評価指標
    """
    # カラム名を小文字に変換
    data_lower = data.copy()
    data_lower.columns = [col.lower() for col in data_lower.columns]
    
    # シグナルを生成
    signals = strategy.generate_signals(data_lower)
    
    # 最初の銘柄のシグナルを取得
    signal_df = signals[list(signals.keys())[0]]
    
    # 評価指標を計算
    # 1. シグナルの数
    buy_signals = (signal_df['signal'] == 1).sum()
    sell_signals = (signal_df['signal'] == -1).sum()
    
    # 2. 単純なバックテスト（各シグナルの次の日のリターンを計算）
    data_with_signals = data_lower.copy()
    data_with_signals['signal'] = signal_df['signal']
    
    # 次の日のリターンを計算
    data_with_signals['next_return'] = data_with_signals['close'].pct_change(1).shift(-1)
    
    # NaNを0に置き換え
    data_with_signals['next_return'] = data_with_signals['next_return'].fillna(0)
    
    # シグナルに基づくリターンを計算
    data_with_signals['strategy_return'] = data_with_signals['signal'] * data_with_signals['next_return']
    
    # 累積リターンを計算
    data_with_signals['cumulative_return'] = (1 + data_with_signals['strategy_return']).cumprod()
    
    # 買い持ち戦略のリターンを計算
    data_with_signals['buy_hold_return'] = (1 + data_with_signals['next_return']).cumprod()
    
    # 最終的なリターン
    final_return = data_with_signals['cumulative_return'].iloc[-1] - 1 if len(data_with_signals) > 0 else 0
    buy_hold_return = data_with_signals['buy_hold_return'].iloc[-1] - 1 if len(data_with_signals) > 0 else 0
    
    # 最終的な資金
    final_capital = initial_capital * (1 + final_return)
    buy_hold_capital = initial_capital * (1 + buy_hold_return)
    
    # 勝率を計算
    winning_trades = (data_with_signals['strategy_return'] > 0).sum()
    total_trades = (data_with_signals['signal'] != 0).sum()
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    
    # 最大ドローダウンを計算
    peak = data_with_signals['cumulative_return'].cummax()
    drawdown = (data_with_signals['cumulative_return'] - peak) / peak
    max_drawdown = drawdown.min()
    
    # シャープレシオを計算（年率）
    returns = data_with_signals['strategy_return']
    sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std() if returns.std() > 0 else 0
    
    # 結果を表示
    print(f"\n{name}データでの {strategy.__class__.__name__} の評価結果:")
    print(f"  買いシグナル数: {buy_signals}")
    print(f"  売りシグナル数: {sell_signals}")
    print(f"  戦略のリターン: {final_return*100:.2f}%")
    print(f"  買い持ち戦略のリターン: {buy_hold_return*100:.2f}%")
    print(f"  初期資金: {initial_capital:,.0f}円")
    print(f"  戦略の最終資金: {final_capital:,.0f}円 ({final_capital - initial_capital:+,.0f}円)")
    print(f"  買い持ち戦略の最終資金: {buy_hold_capital:,.0f}円 ({buy_hold_capital - initial_capital:+,.0f}円)")
    print(f"  勝率: {win_rate*100:.2f}%")
    print(f"  最大ドローダウン: {max_drawdown*100:.2f}%")
    print(f"  シャープレシオ: {sharpe_ratio:.2f}")
    
    # 評価指標を返す
    return {
        'buy_signals': buy_signals,
        'sell_signals': sell_signals,
        'final_return': final_return,
        'buy_hold_return': buy_hold_return,
        'initial_capital': initial_capital,
        'final_capital': final_capital,
        'buy_hold_capital': buy_hold_capital,
        'win_rate': win_rate,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe_ratio,
        'data_with_signals': data_with_signals
    }

def plot_strategy_performance(results: Dict, strategy_name: str, symbol: str, output_dir: str = 'results') -> None:
    """
    戦略のパフォーマンスをプロットする
    
    Parameters:
    -----------
    results : dict
        各データセットの評価結果
    strategy_name : str
        戦略名
    symbol : str
        銘柄シンボル
    output_dir : str
        出力ディレクトリ
    """
    # 出力ディレクトリが存在しない場合は作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    plt.figure(figsize=(12, 8))
    
    # 各データセットの累積リターンをプロット
    for name, result in results.items():
        data = result['data_with_signals']
        plt.plot(data.index, data['cumulative_return'], label=f'{name} - 戦略')
        plt.plot(data.index, data['buy_hold_return'], label=f'{name} - 買い持ち', linestyle='--')
    
    plt.title(f'{symbol} - {strategy_name} - 累積リターン')
    plt.xlabel('日付')
    plt.ylabel('累積リターン')
    plt.legend()
    plt.grid(True)
    
    # 保存
    output_path = os.path.join(output_dir, f'{symbol}_{strategy_name}_performance.png')
    plt.savefig(output_path)
    print(f"パフォーマンスグラフを {output_path} に保存しました。")

def compare_strategies(all_results: Dict, symbol: str, initial_capital: float = 10000, output_dir: str = 'results') -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    戦略間のパフォーマンスを比較する
    
    Parameters:
    -----------
    all_results : dict
        各戦略の評価結果
    symbol : str
        銘柄シンボル
    initial_capital : float
        初期資金
    output_dir : str
        出力ディレクトリ
        
    Returns:
    --------
    tuple
        (検証データの比較表, テストデータの比較表)
    """
    # 出力ディレクトリが存在しない場合は作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # テストデータでの各戦略のパフォーマンスを比較
    test_results = {strategy: results['Test'] for strategy, results in all_results.items()}
    validation_results = {strategy: results['Validation'] for strategy, results in all_results.items()}
    
    # テストデータの比較表を作成
    test_comparison = pd.DataFrame({
        'リターン (%)': {s: r['final_return']*100 for s, r in test_results.items()},
        '買い持ちリターン (%)': {s: r['buy_hold_return']*100 for s, r in test_results.items()},
        '勝率 (%)': {s: r['win_rate']*100 for s, r in test_results.items()},
        '最大ドローダウン (%)': {s: r['max_drawdown']*100 for s, r in test_results.items()},
        'シャープレシオ': {s: r['sharpe_ratio'] for s, r in test_results.items()},
        '買いシグナル数': {s: r['buy_signals'] for s, r in test_results.items()},
        '売りシグナル数': {s: r['sell_signals'] for s, r in test_results.items()},
        '最終資金 (円)': {s: r['final_capital'] for s, r in test_results.items()},
        '損益 (円)': {s: r['final_capital'] - initial_capital for s, r in test_results.items()}
    })
    
    # 検証データの比較表を作成
    validation_comparison = pd.DataFrame({
        'リターン (%)': {s: r['final_return']*100 for s, r in validation_results.items()},
        '買い持ちリターン (%)': {s: r['buy_hold_return']*100 for s, r in validation_results.items()},
        '勝率 (%)': {s: r['win_rate']*100 for s, r in validation_results.items()},
        '最大ドローダウン (%)': {s: r['max_drawdown']*100 for s, r in validation_results.items()},
        'シャープレシオ': {s: r['sharpe_ratio'] for s, r in validation_results.items()},
        '買いシグナル数': {s: r['buy_signals'] for s, r in validation_results.items()},
        '売りシグナル数': {s: r['sell_signals'] for s, r in validation_results.items()},
        '最終資金 (円)': {s: r['final_capital'] for s, r in validation_results.items()},
        '損益 (円)': {s: r['final_capital'] - initial_capital for s, r in validation_results.items()}
    })
    
    print("\n戦略間のパフォーマンス比較（検証データ）:")
    print(validation_comparison)
    
    print("\n戦略間のパフォーマンス比較（テストデータ）:")
    print(test_comparison)
    
    # 比較グラフを作成（テストデータ）
    plt.figure(figsize=(12, 8))
    
    for strategy, result in test_results.items():
        data = result['data_with_signals']
        plt.plot(data.index, data['cumulative_return'], label=f'{strategy}')
    
    # 買い持ち戦略も追加
    plt.plot(data.index, data['buy_hold_return'], label='買い持ち戦略', linestyle='--', color='black')
    
    plt.title(f'{symbol} - 各戦略のパフォーマンス比較（テストデータ）')
    plt.xlabel('日付')
    plt.ylabel('累積リターン')
    plt.legend()
    plt.grid(True)
    
    # 保存
    test_plot_path = os.path.join(output_dir, f'{symbol}_strategy_comparison_test.png')
    plt.savefig(test_plot_path)
    print(f"戦略比較グラフ（テストデータ）を {test_plot_path} に保存しました。")
    
    # 比較グラフを作成（検証データ）
    plt.figure(figsize=(12, 8))
    
    for strategy, result in validation_results.items():
        data = result['data_with_signals']
        plt.plot(data.index, data['cumulative_return'], label=f'{strategy}')
    
    # 買い持ち戦略も追加
    plt.plot(data.index, data['buy_hold_return'], label='買い持ち戦略', linestyle='--', color='black')
    
    plt.title(f'{symbol} - 各戦略のパフォーマンス比較（検証データ）')
    plt.xlabel('日付')
    plt.ylabel('累積リターン')
    plt.legend()
    plt.grid(True)
    
    # 保存
    val_plot_path = os.path.join(output_dir, f'{symbol}_strategy_comparison_validation.png')
    plt.savefig(val_plot_path)
    print(f"戦略比較グラフ（検証データ）を {val_plot_path} に保存しました。")
    
    # 比較表をCSVに保存
    val_csv_path = os.path.join(output_dir, f'{symbol}_strategy_comparison_validation.csv')
    validation_comparison.to_csv(val_csv_path)
    print(f"戦略比較表（検証データ）を {val_csv_path} に保存しました。")
    
    test_csv_path = os.path.join(output_dir, f'{symbol}_strategy_comparison_test.csv')
    test_comparison.to_csv(test_csv_path)
    print(f"戦略比較表（テストデータ）を {test_csv_path} に保存しました。")
    
    return validation_comparison, test_comparison

def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='株価データに対して複数の取引戦略を評価する')
    parser.add_argument('file_path', help='株価データのCSVファイルパス')
    parser.add_argument('--symbol', help='銘柄シンボル（出力ファイル名に使用）', default='STOCK')
    parser.add_argument('--initial-capital', type=float, help='初期資金（円）', default=1000000)
    parser.add_argument('--output-dir', help='出力ディレクトリ', default='results')
    parser.add_argument('--train-size', type=float, help='訓練データの割合', default=0.6)
    parser.add_argument('--val-size', type=float, help='検証データの割合', default=0.2)
    parser.add_argument('--test-size', type=float, help='テストデータの割合', default=0.2)
    args = parser.parse_args()
    
    # 株価データを読み込む
    df = load_stock_data(args.file_path)
    if df is None:
        print("データの読み込みに失敗したため、処理を終了します。")
        return
    
    # データを分割
    train_data, val_data, test_data = split_data(df, args.train_size, args.val_size, args.test_size)
    
    # 戦略を初期化
    strategies = {
        'SimpleMA': SimpleMAStrategy(short_window=5, long_window=20),
        'TripleMA': TripleMAStrategy(short_window=5, mid_window=20, long_window=50),
        'RSI': RSIStrategy(period=14, overbought=70, oversold=30),
        'MACD': MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
    }
    
    # 各戦略の評価結果を保存
    all_results = {}
    
    # 各戦略を評価
    for strategy_name, strategy in strategies.items():
        print(f"\n{strategy_name} を評価中...")
        
        # 各データセットで評価
        results = {
            'Train': evaluate_strategy(strategy, train_data, '訓練', args.initial_capital),
            'Validation': evaluate_strategy(strategy, val_data, '検証', args.initial_capital),
            'Test': evaluate_strategy(strategy, test_data, 'テスト', args.initial_capital)
        }
        
        # パフォーマンスをプロット
        plot_strategy_performance(results, strategy_name, args.symbol, args.output_dir)
        
        # 結果を保存
        all_results[strategy_name] = results
    
    # 戦略間の比較
    validation_comparison, test_comparison = compare_strategies(all_results, args.symbol, args.initial_capital, args.output_dir)
    
    # 検証データとテストデータの結果を比較
    print("\n検証データとテストデータの結果の比較:")
    for strategy in strategies.keys():
        print(f"\n{strategy}:")
        print(f"  検証データ: リターン {validation_comparison.loc[strategy, 'リターン (%)']: .2f}%, 勝率 {validation_comparison.loc[strategy, '勝率 (%)']: .2f}%, シャープレシオ {validation_comparison.loc[strategy, 'シャープレシオ']: .2f}")
        print(f"  テストデータ: リターン {test_comparison.loc[strategy, 'リターン (%)']: .2f}%, 勝率 {test_comparison.loc[strategy, '勝率 (%)']: .2f}%, シャープレシオ {test_comparison.loc[strategy, 'シャープレシオ']: .2f}")

if __name__ == "__main__":
    main()