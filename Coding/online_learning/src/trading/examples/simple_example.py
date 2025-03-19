"""
simple_example.py

取引システムの簡単な使用例
"""

import asyncio
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading.execution.paper_executor import PaperExecutor
from trading.common.strategy_manager import StrategyManager
from trading.common.strategies.simple_ma import SimpleMAStrategy, TripleMAStrategy
from trading.common.strategies.rsi import RSIStrategy
from trading.common.strategies.macd import MACDStrategy

async def run_example():
    """サンプル実行関数"""
    # 設定
    symbol = 'TSLA'
    initial_capital = 1000000
    risk_per_trade = 0.02
    max_position_size = 0.1
    
    print(f"銘柄: {symbol}")
    print(f"初期資金: {initial_capital:,.0f}円")
    
    # ペーパートレードエグゼキューターの初期化
    executor = PaperExecutor(
        initial_capital=initial_capital,
        risk_per_trade=risk_per_trade,
        max_position_size=max_position_size
    )
    
    # 戦略マネージャーの初期化
    strategy_manager = StrategyManager()
    
    # 戦略の登録
    strategy_manager.register_strategy('SimpleMA', SimpleMAStrategy())
    strategy_manager.register_strategy('TripleMA', TripleMAStrategy())
    strategy_manager.register_strategy('RSI', RSIStrategy())
    strategy_manager.register_strategy('MACD', MACDStrategy())
    
    # 使用する戦略の設定
    strategy_manager.set_active_strategy(symbol, 'TripleMA')
    
    print(f"使用する戦略: TripleMA")
    
    # 取引システムの開始
    print("取引システムを開始します...")
    if not await executor.start():
        print("取引システムの開始に失敗しました")
        return
    
    try:
        # 市場データの取得
        print(f"{symbol}の市場データを取得しています...")
        market_data = await executor.get_market_data(symbol)
        
        if market_data is None:
            print(f"{symbol}の市場データを取得できませんでした")
            return
        
        print(f"市場データを取得しました: {len(market_data)}行")
        
        # 戦略の実行
        print("戦略を実行しています...")
        signals = strategy_manager.execute(symbol, market_data)
        
        if not signals or symbol not in signals:
            print(f"{symbol}のシグナルを生成できませんでした")
            return
        
        signal_df = signals[symbol]
        print(f"シグナルを生成しました: {len(signal_df)}行")
        
        # シグナルの可視化
        print("シグナルを可視化しています...")
        visualize_signals(market_data, signal_df, symbol)
        
        # バックテスト
        print("バックテストを実行しています...")
        backtest_results = backtest(market_data, signal_df, initial_capital)
        
        # 結果の表示
        print("\n===== バックテスト結果 =====")
        print(f"初期資金: {initial_capital:,.0f}円")
        print(f"最終資金: {backtest_results['final_capital']:,.0f}円")
        print(f"リターン: {backtest_results['return']:.2%}")
        print(f"取引回数: {backtest_results['trades']}")
        print(f"勝率: {backtest_results['win_rate']:.2%}")
        print(f"最大ドローダウン: {backtest_results['max_drawdown']:.2%}")
        
    finally:
        # 取引システムの停止
        await executor.stop()
        print("取引システムを停止しました")

def visualize_signals(market_data, signal_df, symbol):
    """シグナルの可視化"""
    plt.figure(figsize=(12, 8))
    
    # 価格チャート
    plt.subplot(2, 1, 1)
    plt.plot(market_data.index, market_data['Close'], label='Close Price')
    
    # 移動平均線
    if 'short_ma' in signal_df.columns:
        plt.plot(signal_df.index, signal_df['short_ma'], label='Short MA')
    if 'mid_ma' in signal_df.columns:
        plt.plot(signal_df.index, signal_df['mid_ma'], label='Mid MA')
    if 'long_ma' in signal_df.columns:
        plt.plot(signal_df.index, signal_df['long_ma'], label='Long MA')
    
    # 買いシグナル
    buy_signals = signal_df[signal_df['position'] > 0]
    plt.scatter(buy_signals.index, market_data.loc[buy_signals.index]['Close'], 
                marker='^', color='g', s=100, label='Buy')
    
    # 売りシグナル
    sell_signals = signal_df[signal_df['position'] < 0]
    plt.scatter(sell_signals.index, market_data.loc[sell_signals.index]['Close'], 
                marker='v', color='r', s=100, label='Sell')
    
    plt.title(f'{symbol} Price and Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    
    # シグナル強度
    plt.subplot(2, 1, 2)
    plt.plot(signal_df.index, signal_df['signal'], label='Signal Strength')
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.title('Signal Strength')
    plt.xlabel('Date')
    plt.ylabel('Strength')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    
    # 保存ディレクトリの作成
    os.makedirs('results', exist_ok=True)
    plt.savefig(f'results/{symbol}_signals.png')
    print(f"シグナルチャートを保存しました: results/{symbol}_signals.png")
    
    plt.close()

def backtest(market_data, signal_df, initial_capital):
    """簡易バックテスト"""
    capital = initial_capital
    position = 0
    trades = 0
    wins = 0
    losses = 0
    buy_price = 0
    max_capital = initial_capital
    min_capital = initial_capital
    max_drawdown = 0
    
    # 資金推移
    equity_curve = [initial_capital]
    
    # シグナルに基づいて取引
    for i in range(1, len(signal_df)):
        date = signal_df.index[i]
        price = market_data.loc[date]['Close']
        position_change = signal_df['position'].iloc[i]
        
        # ポジションの変更
        if position_change > 0:  # 買いシグナル
            if position <= 0:  # 新規または売りポジションのクローズ
                # 売りポジションのクローズ
                if position < 0:
                    profit = (buy_price - price) * abs(position)
                    capital += profit
                    if profit > 0:
                        wins += 1
                    else:
                        losses += 1
                    trades += 1
                
                # 新規買いポジション
                position = int((capital * 0.1) / price)  # 資金の10%を使用
                buy_price = price
                capital -= position * price
        
        elif position_change < 0:  # 売りシグナル
            if position >= 0:  # 新規または買いポジションのクローズ
                # 買いポジションのクローズ
                if position > 0:
                    profit = (price - buy_price) * position
                    capital += position * price
                    if profit > 0:
                        wins += 1
                    else:
                        losses += 1
                    trades += 1
                
                # 新規売りポジション
                position = -int((capital * 0.1) / price)  # 資金の10%を使用
                buy_price = price
                capital += abs(position) * price
        
        # 現在の資産評価
        current_equity = capital
        if position > 0:
            current_equity += position * price
        elif position < 0:
            current_equity -= abs(position) * price
        
        equity_curve.append(current_equity)
        
        # 最大資産と最小資産の更新
        max_capital = max(max_capital, current_equity)
        min_capital = min(min_capital, current_equity)
        
        # 最大ドローダウンの計算
        drawdown = (max_capital - current_equity) / max_capital
        max_drawdown = max(max_drawdown, drawdown)
    
    # 最終ポジションのクローズ
    final_price = market_data['Close'].iloc[-1]
    if position > 0:
        profit = (final_price - buy_price) * position
        capital += position * final_price
        if profit > 0:
            wins += 1
        else:
            losses += 1
        trades += 1
    elif position < 0:
        profit = (buy_price - final_price) * abs(position)
        capital += abs(position) * final_price
        if profit > 0:
            wins += 1
        else:
            losses += 1
        trades += 1
    
    # 結果の計算
    final_capital = capital
    total_return = (final_capital - initial_capital) / initial_capital
    win_rate = wins / trades if trades > 0 else 0
    
    # 資金推移のプロット
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(equity_curve)), equity_curve)
    plt.title('Equity Curve')
    plt.xlabel('Trading Days')
    plt.ylabel('Capital')
    plt.grid(True)
    plt.savefig(f'results/equity_curve.png')
    print(f"資金推移チャートを保存しました: results/equity_curve.png")
    plt.close()
    
    return {
        'final_capital': final_capital,
        'return': total_return,
        'trades': trades,
        'win_rate': win_rate,
        'max_drawdown': max_drawdown
    }

if __name__ == "__main__":
    # イベントループの実行
    asyncio.run(run_example())