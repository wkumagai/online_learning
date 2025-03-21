"""
Module for managing trade execution
"""

import logging
from typing import Dict, Optional, List, Union
from datetime import datetime
import asyncio
import pandas as pd
from .ib_executor import IBExecutor

class TradeExecutor:
    """Class for managing trade execution"""
    
    def __init__(
        self,
        initial_capital: float,
        risk_per_trade: float = 0.02,  # Risk per trade (2% of capital)
        max_position_size: float = 0.1,  # Maximum position size (10% of capital)
        paper_trading: bool = True
    ):
        """
        Initialize trade executor
        Args:
            initial_capital: Initial capital
            risk_per_trade: Risk per trade
            max_position_size: Maximum position size
            paper_trading: Whether to use paper trading mode
        """
        self.logger = logging.getLogger(__name__)
        self.initial_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.max_position_size = max_position_size
        self.paper_trading = paper_trading
        
        # Initialize IBKR executor
        self.executor = IBExecutor(paper_trading=paper_trading)
        self.positions = {}
        self.orders = {}

    async def start(self) -> bool:
        """
        Start trade execution system
        Returns:
            Whether startup was successful
        """
        try:
            # Connect to IBKR
            connected = await self.executor.connect()
            if not connected:
                return False

            # Get current positions
            positions = await self.executor.get_positions()
            self.positions = {
                pos['symbol']: pos
                for pos in positions
            }

            self.logger.info("Trade executor started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start trade executor: {str(e)}")
            return False

    async def stop(self):
        """Stop trade execution system"""
        try:
            await self.executor.disconnect()
            self.logger.info("Trade executor stopped")
        except Exception as e:
            self.logger.error(f"Error stopping trade executor: {str(e)}")

    async def execute_signals(
        self,
        signals: Dict[str, pd.DataFrame],
        prices: Dict[str, float]
    ) -> Dict[str, List[Dict]]:
        """
        Execute trading signals
        Args:
            signals: Trading signals for each symbol
            prices: Current prices for each symbol
        Returns:
            Execution results
        """
        results = {}
        
        for symbol, signal_df in signals.items():
            if symbol not in prices:
                continue

            current_price = prices[symbol]
            latest_signal = signal_df.iloc[-1]
            
            # Calculate position size
            size = self._calculate_position_size(
                symbol,
                current_price,
                latest_signal['signal']
            )
            
            if size == 0:
                continue

            # Execute order
            try:
                if size > 0:
                    trade = await self.executor.place_market_order(
                        symbol=symbol,
                        quantity=size,
                        action='BUY'
                    )
                else:
                    trade = await self.executor.place_market_order(
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
                self.logger.error(f"Error executing trade for {symbol}: {str(e)}")
                results[symbol] = [{
                    'timestamp': datetime.now(),
                    'error': str(e),
                    'status': 'failed'
                }]

        return results

    def _calculate_position_size(
        self,
        symbol: str,
        current_price: float,
        signal: float
    ) -> int:
        """
        Calculate position size
        Args:
            symbol: Stock symbol
            current_price: Current price
            signal: Trading signal
        Returns:
            Trade quantity (positive: buy, negative: sell)
        """
        try:
            # Get account information
            account = asyncio.run(self.executor.get_account_summary())
            current_capital = float(account.get('NetLiquidation', {}).get('value', self.initial_capital))
            
            # Calculate trade quantity based on risk
            risk_amount = current_capital * self.risk_per_trade
            max_amount = current_capital * self.max_position_size
            
            # Consider current position
            current_position = self.positions.get(symbol, {}).get('position', 0)
            
            # Determine trade quantity based on signal
            if signal > 0:  # Buy signal
                if current_position >= 0:
                    # New or additional long position
                    max_additional = int(max_amount / current_price) - current_position
                    size = min(
                        int(risk_amount / current_price),
                        max_additional
                    )
                else:
                    # Close short position
                    size = abs(current_position)
            elif signal < 0:  # Sell signal
                if current_position <= 0:
                    # New or additional short position
                    max_additional = int(max_amount / current_price) + current_position
                    size = -min(
                        int(risk_amount / current_price),
                        max_additional
                    )
                else:
                    # Close long position
                    size = -current_position
            else:
                size = 0
            
            return size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return 0

    async def get_current_positions(self) -> Dict[str, Dict]:
        """
        Get current position information
        Returns:
            Position information
        """
        try:
            positions = await self.executor.get_positions()
            self.positions = {
                pos['symbol']: pos
                for pos in positions
            }
            return self.positions
        except Exception as e:
            self.logger.error(f"Error getting positions: {str(e)}")
            return {}
