"""
real_executor.py

実運用モードの取引実行エンジン
"""

import logging
from typing import Dict, Optional, List, Any
from datetime import datetime
import asyncio
import pandas as pd
from ib_insync import *

from trading.execution.base_executor import BaseExecutor

class RealExecutor(BaseExecutor):
    """
    実運用モードの取引実行エンジン
    
    Interactive Brokersを使用して実際の取引を行う
    """
    
    def __init__(
        self,
        initial_capital: float = 1000000,
        risk_per_trade: float = 0.02,
        max_position_size: float = 0.1,
        host: str = '127.0.0.1',
        port: int = 7497,  # TWS: 7497, IB Gateway: 4001
        client_id: int = 1
    ):
        """
        初期化
        
        Args:
            initial_capital: 初期資金
            risk_per_trade: 1トレードあたりのリスク（資金に対する割合）
            max_position_size: 最大ポジションサイズ（資金に対する割合）
            host: IBKRサーバーホスト
            port: IBKRサーバーポート
            client_id: クライアントID
        """
        super().__init__(initial_capital, risk_per_trade, max_position_size)
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()
        self.connected = False
        self.positions = {}
        self.orders = {}
    
    async def start(self) -> bool:
        """
        実行エンジンを開始
        
        Returns:
            bool: 開始に成功したかどうか
        """
        try:
            # IBKRに接続
            await self.ib.connectAsync(
                host=self.host,
                port=self.port,
                clientId=self.client_id
            )
            self.connected = True
            self.logger.info("IBKRに接続しました")
            
            # 現在のポジションを取得
            positions = await self.get_current_positions()
            self.logger.info(f"現在のポジション: {positions}")
            
            return True
        except Exception as e:
            self.logger.error(f"実行エンジンの開始に失敗しました: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """
        実行エンジンを停止
        
        Returns:
            bool: 停止に成功したかどうか
        """
        try:
            if self.connected:
                await self.ib.disconnectAsync()
                self.connected = False
                self.logger.info("IBKRから切断しました")
            return True
        except Exception as e:
            self.logger.error(f"実行エンジンの停止に失敗しました: {str(e)}")
            return False
    
    async def get_account_summary(self) -> Dict[str, Any]:
        """
        口座情報を取得
        
        Returns:
            Dict: 口座情報
        """
        if not self.connected:
            self.logger.error("IBKRに接続されていません")
            return {}
        
        try:
            account_values = self.ib.accountSummary()
            summary = {}
            for av in account_values:
                summary[av.tag] = {
                    'value': av.value,
                    'currency': av.currency
                }
            return summary
        except Exception as e:
            self.logger.error(f"口座情報の取得に失敗しました: {str(e)}")
            return {}
    
    async def get_current_positions(self) -> Dict[str, Dict[str, Any]]:
        """
        現在のポジションを取得
        
        Returns:
            Dict: 銘柄ごとのポジション情報
        """
        if not self.connected:
            self.logger.error("IBKRに接続されていません")
            return {}
        
        try:
            positions = self.ib.positions()
            result = {}
            for pos in positions:
                result[pos.contract.symbol] = {
                    'position': pos.position,
                    'avg_price': pos.avgCost,
                    'market_value': pos.marketValue if hasattr(pos, 'marketValue') else None
                }
            self.positions = result
            return result
        except Exception as e:
            self.logger.error(f"ポジション情報の取得に失敗しました: {str(e)}")
            return {}
    
    async def execute_signals(
        self,
        signals: Dict[str, pd.DataFrame],
        current_prices: Dict[str, float]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        取引シグナルを実行
        
        Args:
            signals: 銘柄ごとの取引シグナル
            current_prices: 銘柄ごとの現在価格
            
        Returns:
            Dict: 銘柄ごとの取引結果
        """
        results = {}
        
        for symbol, signal_df in signals.items():
            if symbol not in current_prices:
                continue
            
            current_price = current_prices[symbol]
            latest_signal = signal_df.iloc[-1]
            
            # ポジションサイズの計算
            size = self._calculate_position_size(
                symbol,
                current_price,
                latest_signal['signal']
            )
            
            if size == 0:
                continue
            
            # 注文の実行
            try:
                if size > 0:
                    trade = await self._place_market_order(
                        symbol=symbol,
                        quantity=size,
                        action='BUY'
                    )
                else:
                    trade = await self._place_market_order(
                        symbol=symbol,
                        quantity=abs(size),
                        action='SELL'
                    )
                
                if trade:
                    results[symbol] = [{
                        'timestamp': datetime.now(),
                        'action': 'BUY' if size > 0 else 'SELL',
                        'quantity': abs(size),
                        'price': current_price,
                        'status': 'executed'
                    }]
                    
            except Exception as e:
                self.logger.error(f"{symbol}の取引実行中にエラーが発生しました: {str(e)}")
                results[symbol] = [{
                    'timestamp': datetime.now(),
                    'error': str(e),
                    'status': 'failed'
                }]
        
        return results
    
    async def get_market_data(
        self,
        symbol: str,
        timeframe: str = '1d',
        bars: int = 100
    ) -> Optional[pd.DataFrame]:
        """
        市場データを取得
        
        Args:
            symbol: 銘柄シンボル
            timeframe: 時間枠
            bars: バー数
            
        Returns:
            DataFrame or None: 市場データ
        """
        if not self.connected:
            self.logger.error("IBKRに接続されていません")
            return None
        
        try:
            # 時間枠の変換
            duration_str = '100 D'
            bar_size = '1 day'
            
            if timeframe == '1h':
                duration_str = f"{bars * 3} D"
                bar_size = '1 hour'
            elif timeframe == '1m':
                duration_str = f"{bars // 60 + 1} D"
                bar_size = '1 min'
            
            # 市場データの取得
            contract = self._create_contract(symbol)
            bars_data = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=duration_str,
                barSizeSetting=bar_size,
                whatToShow='TRADES',
                useRTH=True
            )
            
            if not bars_data:
                self.logger.warning(f"{symbol}の市場データがありません")
                return None
            
            # DataFrameに変換
            df = pd.DataFrame({
                'Date': [bar.date for bar in bars_data],
                'Open': [bar.open for bar in bars_data],
                'High': [bar.high for bar in bars_data],
                'Low': [bar.low for bar in bars_data],
                'Close': [bar.close for bar in bars_data],
                'Volume': [bar.volume for bar in bars_data]
            })
            
            df.set_index('Date', inplace=True)
            return df
            
        except Exception as e:
            self.logger.error(f"{symbol}の市場データ取得中にエラーが発生しました: {str(e)}")
            return None
    
    def _create_contract(
        self,
        symbol: str,
        sec_type: str = 'STK',
        exchange: str = 'SMART',
        currency: str = 'USD'
    ) -> Contract:
        """
        取引用のコントラクトを作成
        
        Args:
            symbol: 銘柄シンボル
            sec_type: 証券タイプ
            exchange: 取引所
            currency: 通貨
        
        Returns:
            Contract: コントラクトオブジェクト
        """
        contract = Contract()
        contract.symbol = symbol
        contract.secType = sec_type
        contract.exchange = exchange
        contract.currency = currency
        return contract
    
    async def _place_market_order(
        self,
        symbol: str,
        quantity: int,
        action: str = 'BUY'
    ) -> Optional[Trade]:
        """
        成行注文を出す
        
        Args:
            symbol: 銘柄シンボル
            quantity: 数量
            action: 'BUY'または'SELL'
        
        Returns:
            Trade: 取引オブジェクト
        """
        if not self.connected:
            self.logger.error("IBKRに接続されていません")
            return None
        
        try:
            contract = self._create_contract(symbol)
            order = MarketOrder(action, abs(quantity))
            trade = self.ib.placeOrder(contract, order)
            self.logger.info(f"成行注文を出しました: {symbol} {action} {quantity}")
            return trade
        except Exception as e:
            self.logger.error(f"成行注文の発注に失敗しました: {str(e)}")
            return None
    
    def _calculate_position_size(
        self,
        symbol: str,
        current_price: float,
        signal: float
    ) -> int:
        """
        ポジションサイズを計算
        
        Args:
            symbol: 銘柄シンボル
            current_price: 現在価格
            signal: 取引シグナル
        
        Returns:
            int: 取引数量（正: 買い、負: 売り）
        """
        try:
            # 口座情報の取得
            account = asyncio.run(self.get_account_summary())
            current_capital = float(account.get('NetLiquidation', {}).get('value', self.initial_capital))
            
            # リスクに基づく取引数量の計算
            risk_amount = current_capital * self.risk_per_trade
            max_amount = current_capital * self.max_position_size
            
            # 現在のポジションを考慮
            current_position = self.positions.get(symbol, {}).get('position', 0)
            
            # シグナルに基づく取引数量の決定
            if signal > 0:  # 買いシグナル
                if current_position >= 0:
                    # 新規または追加の買いポジション
                    max_additional = int(max_amount / current_price) - current_position
                    size = min(
                        int(risk_amount / current_price),
                        max_additional
                    )
                else:
                    # 売りポジションのクローズ
                    size = abs(current_position)
            elif signal < 0:  # 売りシグナル
                if current_position <= 0:
                    # 新規または追加の売りポジション
                    max_additional = int(max_amount / current_price) + current_position
                    size = -min(
                        int(risk_amount / current_price),
                        max_additional
                    )
                else:
                    # 買いポジションのクローズ
                    size = -current_position
            else:
                size = 0
            
            return size
            
        except Exception as e:
            self.logger.error(f"ポジションサイズの計算中にエラーが発生しました: {str(e)}")
            return 0
