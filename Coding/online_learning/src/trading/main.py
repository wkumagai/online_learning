"""
main.py

取引システムのメインエントリーポイント
実運用モードとペーパートレードモードを切り替え可能
"""

import asyncio
import argparse
import logging
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

# 環境変数の読み込み
load_dotenv()

# ロギングの設定
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'logs/trading_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 戦略マネージャーのインポート
from trading.common.strategy_manager import StrategyManager
from trading.common.strategies.simple_ma import SimpleMAStrategy, TripleMAStrategy
from trading.common.strategies.rsi import RSIStrategy, RSIWithTrendStrategy
from trading.common.strategies.macd import MACDStrategy, MACDHistogramStrategy, MACDDivergenceStrategy

async def main():
    """メイン関数"""
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='取引システム')
    parser.add_argument('--mode', choices=['paper', 'real'], default='paper',
                      help='実行モード: paper (ペーパートレード) または real (実運用)')
    parser.add_argument('--capital', type=float, default=1000000,
                      help='初期資金 (デフォルト: 1,000,000)')
    parser.add_argument('--risk', type=float, default=0.02,
                      help='1トレードあたりのリスク (デフォルト: 0.02)')
    parser.add_argument('--max-position', type=float, default=0.1,
                      help='最大ポジションサイズ (デフォルト: 0.1)')
    parser.add_argument('--symbols', default='NVDA',
                      help='対象銘柄 (カンマ区切り)')
    parser.add_argument('--strategy', default='TripleMA',
                      help='使用する戦略 (デフォルト: TripleMA)')
    parser.add_argument('--interval', type=int, default=60,
                      help='更新間隔（秒） (デフォルト: 60)')
    args = parser.parse_args()
    
    # 実行モードに応じたエグゼキューターを初期化
    if args.mode == 'paper':
        from trading.execution.paper_executor import PaperExecutor
        executor = PaperExecutor(
            initial_capital=args.capital,
            risk_per_trade=args.risk,
            max_position_size=args.max_position
        )
        logger.info("ペーパートレードモードで起動します")
    else:
        from trading.execution.real_executor import RealExecutor
        executor = RealExecutor(
            initial_capital=args.capital,
            risk_per_trade=args.risk,
            max_position_size=args.max_position
        )
        logger.info("実運用モードで起動します")
    
    # 対象銘柄の設定
    symbols = args.symbols.split(',')
    logger.info(f"対象銘柄: {symbols}")
    
    # 戦略マネージャーの初期化
    strategy_manager = StrategyManager()
    
    # 戦略の登録
    strategy_manager.register_strategy('SimpleMA', SimpleMAStrategy())
    strategy_manager.register_strategy('TripleMA', TripleMAStrategy())
    strategy_manager.register_strategy('RSI', RSIStrategy())
    strategy_manager.register_strategy('RSIWithTrend', RSIWithTrendStrategy())
    strategy_manager.register_strategy('MACD', MACDStrategy())
    strategy_manager.register_strategy('MACDHistogram', MACDHistogramStrategy())
    strategy_manager.register_strategy('MACDDivergence', MACDDivergenceStrategy())
    
    # 使用する戦略の設定
    for symbol in symbols:
        strategy_manager.set_active_strategy(symbol, args.strategy)
    
    logger.info(f"使用する戦略: {args.strategy}")
    
    try:
        # 取引システムの開始
        logger.info("取引システムを開始します...")
        if not await executor.start():
            logger.error("取引システムの開始に失敗しました")
            return
        
        logger.info(f"初期資金: {args.capital:,.0f}円")
        
        # メインループ
        while True:
            try:
                # 口座情報の取得と表示
                account = await executor.get_account_summary()
                current_equity = float(account.get('NetLiquidation', {}).get('value', args.capital))
                profit_loss = current_equity - args.capital
                logger.info(f"現在の資産: {current_equity:,.0f}円 (損益: {profit_loss:+,.0f}円)")
                
                # 現在のポジションを取得
                positions = await executor.get_current_positions()
                if positions:
                    logger.info("現在のポジション:")
                    for symbol, pos in positions.items():
                        logger.info(f"  {symbol}: {pos['position']} 株 (平均取得価格: {pos.get('avg_price', 0):,.2f}円)")
                else:
                    logger.info("現在のポジション: なし")
                
                # 各銘柄の処理
                for symbol in symbols:
                    # 市場データの取得
                    market_data = await executor.get_market_data(symbol)
                    if market_data is None:
                        logger.warning(f"{symbol} の市場データを取得できませんでした")
                        continue
                    
                    # 戦略の実行
                    signals = strategy_manager.execute(symbol, market_data)
                    
                    if not signals or symbol not in signals:
                        logger.warning(f"{symbol} のシグナルを生成できませんでした")
                        continue
                    
                    # 最新のシグナルを取得
                    latest_signal = signals[symbol].iloc[-1]
                    signal_value = latest_signal['signal']
                    
                    logger.info(f"{symbol} の最新シグナル: {signal_value}")
                    
                    # シグナルに基づいて取引を実行
                    if abs(signal_value) > 0:
                        # 現在価格の取得
                        current_prices = {symbol: market_data['Close'].iloc[-1]}
                        
                        # シグナルの実行
                        results = await executor.execute_signals(signals, current_prices)
                        
                        # 結果の表示
                        if results and symbol in results:
                            for result in results[symbol]:
                                if result['status'] == 'executed':
                                    logger.info(f"取引を実行しました: {symbol} {result['action']} {result['quantity']} @ {result['price']:,.2f}")
                                else:
                                    logger.warning(f"取引に失敗しました: {symbol} - {result.get('error', '不明なエラー')}")
                
                # 指定された間隔で待機
                await asyncio.sleep(args.interval)
                
            except Exception as e:
                logger.error(f"メインループでエラーが発生しました: {str(e)}")
                await asyncio.sleep(args.interval)
        
    except KeyboardInterrupt:
        logger.info("取引システムを停止します...")
    finally:
        # 取引システムの停止
        await executor.stop()
        logger.info("取引システムを停止しました")

if __name__ == "__main__":
    # イベントループの実行
    asyncio.run(main())