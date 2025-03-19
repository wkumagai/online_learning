"""
evaluation.py

バックテストやリアルタイム評価ロジックの実装。
"""

import os
import json
import logging
import datetime
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
import sys

# 他のモジュールをインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategy.strategy import Strategy, load_existing_strategies, generate_signal, safe_rule_check

# ロギングの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ファイルハンドラの設定
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = logging.FileHandler('logs/evaluation.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# コンソールハンドラの設定
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)


class BacktestResult:
    """バックテスト結果を保持するクラス"""
    
    def __init__(self, strategy_name: str, symbol: str, start_date: str, end_date: str):
        """
        Parameters:
        -----------
        strategy_name : str
            戦略の名前
        symbol : str
            銘柄シンボル
        start_date : str
            開始日
        end_date : str
            終了日
        """
        self.strategy_name = strategy_name
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.trades = []
        self.equity_curve = pd.DataFrame()
        self.metrics = {}
        self.created_at = datetime.datetime.now()
    
    def add_trade(self, trade: Dict[str, Any]) -> None:
        """
        取引を追加する
        
        Parameters:
        -----------
        trade : Dict[str, Any]
            取引情報
        """
        self.trades.append(trade)
    
    def set_equity_curve(self, equity_curve: pd.DataFrame) -> None:
        """
        資産曲線を設定する
        
        Parameters:
        -----------
        equity_curve : pd.DataFrame
            資産曲線のデータフレーム
        """
        self.equity_curve = equity_curve
    
    def set_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        評価指標を設定する
        
        Parameters:
        -----------
        metrics : Dict[str, Any]
            評価指標
        """
        self.metrics = metrics
    
    def save(self, directory: str = "data/evaluation/backtest_results") -> str:
        """
        バックテスト結果を保存する
        
        Parameters:
        -----------
        directory : str, optional
            保存先ディレクトリ
        
        Returns:
        --------
        str
            保存したファイルのパス
        """
        # ディレクトリの作成
        os.makedirs(directory, exist_ok=True)
        
        # ファイル名の生成
        timestamp = self.created_at.strftime("%Y%m%d_%H%M%S")
        filename = f"{self.strategy_name}_{self.symbol}_{timestamp}"
        
        # 結果の保存
        result_path = os.path.join(directory, f"{filename}.json")
        
        # JSONに変換可能なデータを作成
        result_data = {
            "strategy_name": self.strategy_name,
            "symbol": self.symbol,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "trades": self.trades,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat()
        }
        
        # JSONに保存
        with open(result_path, "w") as f:
            json.dump(result_data, f, indent=2)
        
        # 資産曲線の保存
        if not self.equity_curve.empty:
            equity_path = os.path.join(directory, f"{filename}_equity.csv")
            self.equity_curve.to_csv(equity_path)
        
        logger.info(f"バックテスト結果を保存しました: {result_path}")
        return result_path
    
    @classmethod
    def load(cls, file_path: str) -> 'BacktestResult':
        """
        保存されたバックテスト結果を読み込む
        
        Parameters:
        -----------
        file_path : str
            読み込むファイルのパス
        
        Returns:
        --------
        BacktestResult
            読み込んだバックテスト結果
        """
        # JSONから読み込み
        with open(file_path, "r") as f:
            data = json.load(f)
        
        # インスタンスの作成
        result = cls(
            data["strategy_name"],
            data["symbol"],
            data["start_date"],
            data["end_date"]
        )
        
        # データの設定
        result.trades = data["trades"]
        result.metrics = data["metrics"]
        result.created_at = datetime.datetime.fromisoformat(data["created_at"])
        
        # 資産曲線の読み込み
        equity_path = file_path.replace(".json", "_equity.csv")
        if os.path.exists(equity_path):
            result.equity_curve = pd.read_csv(equity_path, parse_dates=["date"])
        
        logger.info(f"バックテスト結果を読み込みました: {file_path}")
        return result


def backtest_strategy(
    strategy: Strategy,
    data: pd.DataFrame,
    initial_capital: float = 1000000,
    position_size: float = 0.1,
    commission_rate: float = 0.001,
    slippage_model: Optional[Callable] = None,
    safe_rules: Optional[Dict[str, Dict[str, Any]]] = None
) -> BacktestResult:
    """
    戦略のバックテストを実行する関数
    
    Parameters:
    -----------
    strategy : Strategy
        バックテストする戦略
    data : pd.DataFrame
        株価データ
    initial_capital : float, optional
        初期資金
    position_size : float, optional
        ポジションサイズ（資金に対する割合）
    commission_rate : float, optional
        手数料率
    slippage_model : Callable, optional
        スリッページモデル
    safe_rules : Dict[str, Dict[str, Any]], optional
        適用するsafe-rule
    
    Returns:
    --------
    BacktestResult
        バックテスト結果
    """
    logger.info(f"バックテスト開始: {strategy.name}")
    
    # データの確認
    if data.empty:
        logger.error("データが空です")
        return None
    
    # 必要なカラムの確認
    required_columns = ["date", "open", "high", "low", "close", "volume"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        logger.error(f"必要なカラムがありません: {missing_columns}")
        return None
    
    # データのコピーを作成
    df = data.copy()
    
    # 日付でソート
    df = df.sort_values("date")
    
    # シグナルの生成
    df = generate_signal(strategy, df)
    
    # safe-ruleの適用
    if safe_rules:
        df = safe_rule_check(df, safe_rules)
    
    # バックテスト結果の初期化
    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "unknown"
    start_date = df["date"].min().strftime("%Y-%m-%d")
    end_date = df["date"].max().strftime("%Y-%m-%d")
    
    result = BacktestResult(strategy.name, symbol, start_date, end_date)
    
    # バックテストの実行
    capital = initial_capital
    position = 0
    entry_price = 0
    equity = [capital]
    dates = [df["date"].iloc[0]]
    trades = []
    
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        date = row["date"]
        
        # 前日の終値で評価
        if position != 0:
            capital = capital + position * (row["close"] - prev_row["close"])
        
        # シグナルに基づく取引
        signal = prev_row["signal"]
        
        if signal > 0 and position <= 0:  # 買いシグナル
            # ポジションサイズの計算
            size = (capital * position_size) / row["open"]
            
            # スリッページの適用
            execution_price = row["open"]
            if slippage_model:
                execution_price = slippage_model(row["open"], "buy", size, row)
            
            # 手数料の計算
            commission = execution_price * size * commission_rate
            
            # 取引の実行
            old_position = position
            position = size
            entry_price = execution_price
            
            # 資金の更新
            capital = capital - (execution_price * size) - commission
            
            # 取引の記録
            trade = {
                "date": date.strftime("%Y-%m-%d"),
                "action": "buy",
                "price": execution_price,
                "size": size,
                "commission": commission,
                "old_position": old_position,
                "new_position": position,
                "capital": capital
            }
            trades.append(trade)
            result.add_trade(trade)
            
            logger.debug(f"買い: {date.strftime('%Y-%m-%d')}, 価格: {execution_price}, サイズ: {size}")
            
        elif signal < 0 and position >= 0:  # 売りシグナル
            # ポジションサイズの計算
            size = position if position > 0 else (capital * position_size) / row["open"]
            
            # スリッページの適用
            execution_price = row["open"]
            if slippage_model:
                execution_price = slippage_model(row["open"], "sell", size, row)
            
            # 手数料の計算
            commission = execution_price * size * commission_rate
            
            # 取引の実行
            old_position = position
            position = 0 if position > 0 else -size
            entry_price = execution_price if position < 0 else 0
            
            # 資金の更新
            capital = capital + (execution_price * size) - commission
            
            # 取引の記録
            trade = {
                "date": date.strftime("%Y-%m-%d"),
                "action": "sell",
                "price": execution_price,
                "size": size,
                "commission": commission,
                "old_position": old_position,
                "new_position": position,
                "capital": capital
            }
            trades.append(trade)
            result.add_trade(trade)
            
            logger.debug(f"売り: {date.strftime('%Y-%m-%d')}, 価格: {execution_price}, サイズ: {size}")
        
        # 資産の記録
        equity.append(capital + position * row["close"])
        dates.append(date)
    
    # 資産曲線の作成
    equity_curve = pd.DataFrame({
        "date": dates,
        "equity": equity
    })
    
    # 評価指標の計算
    metrics = calculate_metrics(equity_curve, trades, initial_capital)
    
    # 結果の設定
    result.set_equity_curve(equity_curve)
    result.set_metrics(metrics)
    
    logger.info(f"バックテスト完了: {strategy.name}")
    logger.info(f"総リターン: {metrics['total_return']:.2%}, シャープレシオ: {metrics['sharpe_ratio']:.2f}, 最大ドローダウン: {metrics['max_drawdown']:.2%}")
    
    return result


def realtime_evaluation(
    strategy: Strategy,
    data: pd.DataFrame,
    lookback_period: int = 20,
    safe_rules: Optional[Dict[str, Dict[str, Any]]] = None
) -> pd.DataFrame:
    """
    リアルタイム評価を行う関数
    
    Parameters:
    -----------
    strategy : Strategy
        評価する戦略
    data : pd.DataFrame
        株価データ
    lookback_period : int, optional
        評価に使用する過去のデータ期間
    safe_rules : Dict[str, Dict[str, Any]], optional
        適用するsafe-rule
    
    Returns:
    --------
    pd.DataFrame
        評価結果
    """
    logger.info(f"リアルタイム評価開始: {strategy.name}")
    
    # データの確認
    if data.empty:
        logger.error("データが空です")
        return pd.DataFrame()
    
    # 必要なカラムの確認
    required_columns = ["date", "open", "high", "low", "close", "volume"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        logger.error(f"必要なカラムがありません: {missing_columns}")
        return pd.DataFrame()
    
    # データのコピーを作成
    df = data.copy()
    
    # 日付でソート
    df = df.sort_values("date")
    
    # 最新のデータを取得
    latest_data = df.iloc[-lookback_period:].copy()
    
    # シグナルの生成
    latest_data = generate_signal(strategy, latest_data)
    
    # safe-ruleの適用
    if safe_rules:
        latest_data = safe_rule_check(latest_data, safe_rules)
    
    # 最新のシグナル
    latest_signal = latest_data["signal"].iloc[-1]
    
    # 評価結果の作成
    result = pd.DataFrame({
        "date": [latest_data["date"].iloc[-1]],
        "strategy": [strategy.name],
        "signal": [latest_signal],
        "close": [latest_data["close"].iloc[-1]],
        "evaluation_time": [datetime.datetime.now()]
    })
    
    # 短期パフォーマンスの計算
    if len(latest_data) >= 5:
        result["return_5d"] = latest_data["close"].pct_change(5).iloc[-1]
    
    if len(latest_data) >= 10:
        result["return_10d"] = latest_data["close"].pct_change(10).iloc[-1]
    
    logger.info(f"リアルタイム評価完了: {strategy.name}, シグナル: {latest_signal}")
    
    return result


def calculate_metrics(
    equity_curve: pd.DataFrame,
    trades: List[Dict[str, Any]],
    initial_capital: float
) -> Dict[str, Any]:
    """
    パフォーマンス指標を計算する関数
    
    Parameters:
    -----------
    equity_curve : pd.DataFrame
        資産曲線
    trades : List[Dict[str, Any]]
        取引履歴
    initial_capital : float
        初期資金
    
    Returns:
    --------
    Dict[str, Any]
        計算された指標
    """
    # 基本的な指標
    final_equity = equity_curve["equity"].iloc[-1]
    total_return = (final_equity / initial_capital) - 1
    
    # 日次リターンの計算
    equity_curve["daily_return"] = equity_curve["equity"].pct_change()
    
    # 年率リターンの計算
    days = (equity_curve["date"].iloc[-1] - equity_curve["date"].iloc[0]).days
    annual_return = (1 + total_return) ** (365 / days) - 1
    
    # ボラティリティの計算
    daily_volatility = equity_curve["daily_return"].std()
    annual_volatility = daily_volatility * np.sqrt(252)
    
    # シャープレシオの計算
    risk_free_rate = 0.0  # リスクフリーレートは0と仮定
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
    
    # ドローダウンの計算
    equity_curve["peak"] = equity_curve["equity"].cummax()
    equity_curve["drawdown"] = (equity_curve["equity"] - equity_curve["peak"]) / equity_curve["peak"]
    max_drawdown = equity_curve["drawdown"].min()
    
    # カルマーレシオの計算
    calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown < 0 else 0
    
    # 取引関連の指標
    num_trades = len(trades)
    
    if num_trades > 0:
        # 勝率の計算
        winning_trades = [t for t in trades if (t["action"] == "buy" and t["price"] < equity_curve["equity"].iloc[-1]) or
                          (t["action"] == "sell" and t["price"] > equity_curve["equity"].iloc[-1])]
        win_rate = len(winning_trades) / num_trades
        
        # 平均利益と平均損失の計算
        profits = [t["price"] * t["size"] - t["commission"] for t in winning_trades]
        losses = [t["price"] * t["size"] + t["commission"] for t in trades if t not in winning_trades]
        
        avg_profit = np.mean(profits) if profits else 0
        avg_loss = np.mean(losses) if losses else 0
        
        # 損益比の計算
        profit_loss_ratio = avg_profit / abs(avg_loss) if avg_loss != 0 else 0
    else:
        win_rate = 0
        avg_profit = 0
        avg_loss = 0
        profit_loss_ratio = 0
    
    # 指標の辞書を作成
    metrics = {
        "initial_capital": initial_capital,
        "final_equity": final_equity,
        "total_return": total_return,
        "annual_return": annual_return,
        "daily_volatility": daily_volatility,
        "annual_volatility": annual_volatility,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "calmar_ratio": calmar_ratio,
        "num_trades": num_trades,
        "win_rate": win_rate,
        "avg_profit": avg_profit,
        "avg_loss": avg_loss,
        "profit_loss_ratio": profit_loss_ratio
    }
    
    return metrics


def apply_slippage(
    price: float,
    side: str,
    size: float,
    data: pd.DataFrame,
    model_type: str = "fixed",
    fixed_pct: float = 0.001,
    volatility_factor: float = 0.1,
    volume_factor: float = 0.01
) -> float:
    """
    スリッページを適用する関数
    
    Parameters:
    -----------
    price : float
        注文価格
    side : str
        取引サイド（"buy" または "sell"）
    size : float
        取引サイズ
    data : pd.DataFrame
        市場データ
    model_type : str, optional
        スリッページモデルの種類（"fixed", "volatility", "volume"）
    fixed_pct : float, optional
        固定スリッページ率
    volatility_factor : float, optional
        ボラティリティ係数
    volume_factor : float, optional
        出来高係数
    
    Returns:
    --------
    float
        スリッページ適用後の価格
    """
    # 固定スリッページモデル
    if model_type == "fixed":
        if side == "buy":
            return price * (1 + fixed_pct)
        else:  # sell
            return price * (1 - fixed_pct)
    
    # ボラティリティベースのスリッページモデル
    elif model_type == "volatility":
        # ATRの計算（または既存のATRカラムを使用）
        if "atr" in data:
            atr = data["atr"]
        else:
            high_low = data["high"] - data["low"]
            high_close = abs(data["high"] - data["close"].shift(1))
            low_close = abs(data["low"] - data["close"].shift(1))
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean().iloc[-1]
        
        # スリッページの計算
        slippage_pct = atr / price * volatility_factor
        
        if side == "buy":
            return price * (1 + slippage_pct)
        else:  # sell
            return price * (1 - slippage_pct)
    
    # 出来高ベースのスリッページモデル
    elif model_type == "volume":
        # 出来高に対する注文サイズの比率
        volume_ratio = size / data["volume"]
        
        # スリッページの計算
        slippage_pct = volume_ratio * volume_factor
        
        if side == "buy":
            return price * (1 + slippage_pct)
        else:  # sell
            return price * (1 - slippage_pct)
    
    else:
        logger.error(f"未対応のスリッページモデル: {model_type}")
        return price


def visualize_backtest_result(result: BacktestResult, save_path: Optional[str] = None) -> None:
    """
    バックテスト結果を可視化する関数
    
    Parameters:
    -----------
    result : BacktestResult
        可視化するバックテスト結果
    save_path : str, optional
        保存先のパス
    """
    if result is None or result.equity_curve.empty:
        logger.error("可視化するデータがありません")
        return
    
    # フォントの設定
    plt.rcParams['font.size'] = 12
    
    # 図の作成
    fig, axes = plt.subplots(3, 1, figsize=(12, 15), gridspec_kw={'height_ratios': [3, 1, 1]})
    
    # 資産曲線のプロット
    axes[0].plot(result.equity_curve["date"], result.equity_curve["equity"], label="Equity")
    axes[0].set_title(f"Backtest Result: {result.strategy_name} on {result.symbol}")
    axes[0].set_xlabel("Date")
    axes[0].set_ylabel("Equity")
    axes[0].grid(True)
    axes[0].legend()
    
    # ドローダウンのプロット
    if "drawdown" in result.equity_curve.columns:
        axes[1].fill_between(
            result.equity_curve["date"],
            result.equity_curve["drawdown"] * 100,
            0,
            color="red",
            alpha=0.3
        )
        axes[1].set_xlabel("Date")
        axes[1].set_ylabel("Drawdown (%)")
        axes[1].grid(True)
    
    # 取引のプロット
    if result.trades:
        buy_dates = [datetime.datetime.strptime(t["date"], "%Y-%m-%d") for t in result.trades if t["action"] == "buy"]
        buy_prices = [t["price"] for t in result.trades if t["action"] == "buy"]
        
        sell_dates = [datetime.datetime.strptime(t["date"], "%Y-%m-%d") for t in result.trades if t["action"] == "sell"]
        sell_prices = [t["price"] for t in result.trades if t["action"] == "sell"]
        
        axes[2].scatter(buy_dates, buy_prices, color="green", marker="^", label="Buy")
        axes[2].scatter(sell_dates, sell_prices, color="red", marker="v", label="Sell")
        axes[2].set_xlabel("Date")
        axes[2].set_ylabel("Price")
        axes[2].grid(True)
        axes[2].legend()
    
    # 指標の表示
    metrics_text = "\n".join([
        f"Total Return: {result.metrics['total_return']:.2%}",
        f"Annual Return: {result.metrics['annual_return']:.2%}",
        f"Sharpe Ratio: {result.metrics['sharpe_ratio']:.2f}",
        f"Max Drawdown: {result.metrics['max_drawdown']:.2%}",
        f"Win Rate: {result.metrics['win_rate']:.2%}",
        f"Profit/Loss Ratio: {result.metrics['profit_loss_ratio']:.2f}",
        f"Number of Trades: {result.metrics['num_trades']}"
    ])
    
    plt.figtext(0.15, 0.01, metrics_text, fontsize=12, bbox={"facecolor": "white", "alpha": 0.8, "pad": 5})
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)
    
    # 保存または表示
    if save_path:
        plt.savefig(save_path)
        logger.info(f"バックテスト結果のグラフを保存しました: {save_path}")
    else:
        plt.show()


def compare_strategies(
    results: List[BacktestResult],
    save_path: Optional[str] = None
) -> pd.DataFrame:
    """
    複数の戦略のバックテスト結果を比較する関数
    
    Parameters:
    -----------
    results : List[BacktestResult]
        比較するバックテスト結果のリスト
    save_path : str, optional
        保存先のパス
    
    Returns:
    --------
    pd.DataFrame
        比較結果
    """
    if not results:
        logger.error("比較するデータがありません")
        return pd.DataFrame()
    
    # 比較用のデータフレームを作成
    comparison = pd.DataFrame({
        "Strategy": [r.strategy_name for r in results],
        "Symbol": [r.symbol for r in results],
        "Start Date": [r.start_date for r in results],
        "End Date": [r.end_date for r in results],
        "Total Return (%)": [r.metrics["total_return"] * 100 for r in results],
        "Annual Return (%)": [r.metrics["annual_return"] * 100 for r in results],
        "Sharpe Ratio": [r.metrics["sharpe_ratio"] for r in results],
        "Max Drawdown (%)": [r.metrics["max_drawdown"] * 100 for r in results],
        "Win Rate (%)": [r.metrics["win_rate"] * 100 for r in results],
        "Profit/Loss Ratio": [r.metrics["profit_loss_ratio"] for r in results],
        "Number of Trades": [r.metrics["num_trades"] for r in results]
    })
    
    # 資産曲線の比較グラフ
    plt.figure(figsize=(12, 6))
    
    for result in results:
        # 資産を初期資金で正規化
        normalized_equity = result.equity_curve["equity"] / result.equity_curve["equity"].iloc[0]
        plt.plot(result.equity_curve["date"], normalized_equity, label=result.strategy_name)
    
    plt.title("Strategy Comparison: Normalized Equity Curves")
    plt.xlabel("Date")
    plt.ylabel("Normalized Equity")
    plt.grid(True)
    plt.legend()
    
    # 保存または表示
    if save_path:
        plt.savefig(save_path)
        logger.info(f"戦略比較のグラフを保存しました: {save_path}")
    else:
        plt.show()
    
    return comparison


if __name__ == "__main__":
    # 動作確認用のコード
    logger.info("evaluation.py の動作確認を開始します")
    
    # サンプルデータの作成
    dates = pd.date_range(start="2022-01-01", end="2022-12-31")
    n = len(dates)
    
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.normal(0, 1, n))
    
    data = pd.DataFrame({
        "date": dates,
        "open": close - np.random.uniform(0, 1, n),
        "high": close + np.random.uniform(0, 1, n),
        "low": close - np.random.uniform(0, 1, n),
        "close": close,
        "volume": np.random.randint(1000, 10000, n)
    })
    
    # 移動平均の計算
    data["sma_5"] = data["close"].rolling(window=5).mean()
    data["sma_20"] = data["close"].rolling(window=20).mean()
    
    # 戦略の読み込み
    strategies = load_existing_strategies()
    
    if strategies:
        # 最初の戦略を使用
        strategy = next(iter(strategies.values()))
        
        # バックテストの実行
        result = backtest_strategy(
            strategy,
            data,
            initial_capital=1000000,
            position_size=0.1,
            commission_rate=0.001
        )
        
        if result:
            # 結果の保存
            result.save()
            
            # 結果の可視化
            visualize_backtest_result(result)
    else:
        logger.warning("戦略が見つかりません")
    
    logger.info("evaluation.py の動作確認を終了します")