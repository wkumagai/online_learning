import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np

def main():
    # データの読み込み
    data_path = 'data/stock_data.pkl'
    stock_data = pd.read_pickle(data_path)
    
    # プロットのスタイル設定
    sns.set(style="darkgrid")
    plt.rcParams['figure.figsize'] = (14, 8)
    plt.rcParams['font.size'] = 12
    
    # 終値の抽出
    close_prices = stock_data.xs('Close', level=1, axis=1)
    
    # 終値の推移をプロット
    plt.figure(figsize=(14, 8))
    for ticker in close_prices.columns:
        plt.plot(close_prices.index, close_prices[ticker], label=ticker)
    
    plt.title('Stock Price Comparison: Nvidia and TSMC (2020-2025)', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Price (USD)', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)
    
    # x軸の日付フォーマットを設定
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)
    
    # グラフを保存
    plt.tight_layout()
    plt.savefig('data/stock_price_comparison.png', dpi=300)
    print("Stock price comparison chart saved to data/stock_price_comparison.png")
    
    # 正規化した株価推移（2020年1月2日を100とする）
    plt.figure(figsize=(14, 8))
    
    # 最初の日の株価で正規化
    normalized_prices = close_prices / close_prices.iloc[0] * 100
    
    for ticker in normalized_prices.columns:
        plt.plot(normalized_prices.index, normalized_prices[ticker], label=ticker)
    
    plt.title('Normalized Stock Price: Nvidia and TSMC (2020-2025, Jan 2, 2020=100)', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Normalized Price (Jan 2, 2020=100)', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)
    
    # x軸の日付フォーマットを設定
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)
    
    # グラフを保存
    plt.tight_layout()
    plt.savefig('data/normalized_stock_price_comparison.png', dpi=300)
    print("Normalized stock price chart saved to data/normalized_stock_price_comparison.png")
    
    # 日次リターンの計算と可視化
    daily_returns = close_prices.pct_change().dropna()
    
    # 日次リターンのヒストグラム
    plt.figure(figsize=(14, 8))
    
    for ticker in daily_returns.columns:
        sns.histplot(daily_returns[ticker], label=ticker, kde=True, alpha=0.5, bins=50)
    
    plt.title('Daily Returns Distribution: Nvidia and TSMC (2020-2025)', fontsize=16)
    plt.xlabel('Daily Returns (%)', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)
    
    # グラフを保存
    plt.tight_layout()
    plt.savefig('data/daily_returns_distribution.png', dpi=300)
    print("Daily returns distribution chart saved to data/daily_returns_distribution.png")
    
    # 相関係数の計算と表示
    correlation = daily_returns.corr()
    print("\nDaily returns correlation:")
    print(correlation)
    
    # 相関ヒートマップ
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation, annot=True, cmap='coolwarm', vmin=-1, vmax=1, linewidths=0.5)
    plt.title('Daily Returns Correlation: Nvidia and TSMC', fontsize=16)
    
    # グラフを保存
    plt.tight_layout()
    plt.savefig('data/correlation_heatmap.png', dpi=300)
    print("Correlation heatmap saved to data/correlation_heatmap.png")
    
    print("\nVisualization completed. The following files were created:")
    print("- data/stock_price_comparison.png")
    print("- data/normalized_stock_price_comparison.png")
    print("- data/daily_returns_distribution.png")
    print("- data/correlation_heatmap.png")

if __name__ == "__main__":
    main()