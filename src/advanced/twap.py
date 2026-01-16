"""Time-Weighted Average Price (TWAP) strategy implementation."""

import time
from typing import List, Dict, Any
from datetime import datetime
from src.binance_client import BinanceClient, APIError, ConnectionError
from src.logger import BotLogger


class TWAPStrategy:
    """
    Implements Time-Weighted Average Price execution strategy.
    Splits large orders into smaller chunks executed at regular time intervals.
    """
    
    def __init__(self, client: BinanceClient, logger: BotLogger):
        """
        Initialize TWAP strategy with client and logger.
        
        Args:
            client: BinanceClient instance for order execution.
            logger: BotLogger instance for logging.
        """
        self.client = client
        self.logger = logger
    
    def calculate_interval_quantity(self, total_quantity: float, intervals: int) -> float:
        """
        Calculate quantity per interval.
        
        Args:
            total_quantity: Total quantity to be executed.
            intervals: Number of intervals to split the order.
            
        Returns:
            Quantity to execute per interval.
        """
        return total_quantity / intervals
    
    def execute(
        self,
        symbol: str,
        side: str,
        total_quantity: float,
        duration_minutes: int,
        intervals: int = None
    ) -> List[Dict[str, Any]]:
        """
        Execute TWAP strategy by splitting order into time intervals.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            side: Order side ('BUY' or 'SELL').
            total_quantity: Total quantity to execute.
            duration_minutes: Total duration in minutes to spread the orders.
            intervals: Number of intervals (optional, defaults to duration_minutes).
            
        Returns:
            List of executed order responses.
            
        Raises:
            ValueError: If parameters are invalid.
            APIError: If API returns an error.
            ConnectionError: If connection fails.
        """
        # Validate inputs
        if total_quantity <= 0:
            raise ValueError("Total quantity must be positive")
        
        if duration_minutes <= 0:
            raise ValueError("Duration must be positive")
        
        # Default intervals to duration_minutes if not specified
        if intervals is None:
            intervals = duration_minutes
        
        if intervals <= 0:
            raise ValueError("Intervals must be positive")
        
        # Calculate interval parameters
        interval_quantity = self.calculate_interval_quantity(total_quantity, intervals)
        interval_seconds = (duration_minutes * 60) / intervals
        
        self.logger.info(
            'TWAPStrategy',
            f'Starting TWAP execution: {side} {total_quantity} {symbol}',
            {
                'symbol': symbol,
                'side': side,
                'total_quantity': total_quantity,
                'duration_minutes': duration_minutes,
                'intervals': intervals,
                'interval_quantity': interval_quantity,
                'interval_seconds': interval_seconds
            }
        )
        
        executed_orders = []
        start_time = datetime.now()
        
        # Execute orders at intervals
        for i in range(intervals):
            try:
                interval_num = i + 1
                
                self.logger.info(
                    'TWAPStrategy',
                    f'Executing interval {interval_num}/{intervals}',
                    {
                        'interval': interval_num,
                        'total_intervals': intervals,
                        'quantity': interval_quantity
                    }
                )
                
                # Execute market order for this interval
                order_result = self.client.create_market_order(
                    symbol=symbol,
                    side=side,
                    quantity=interval_quantity
                )
                
                executed_orders.append(order_result)
                
                self.logger.info(
                    'TWAPStrategy',
                    f'Interval {interval_num}/{intervals} executed successfully',
                    {
                        'interval': interval_num,
                        'order_id': order_result.get('orderId'),
                        'executed_qty': order_result.get('executedQty'),
                        'avg_price': order_result.get('avgPrice')
                    }
                )
                
                # Sleep until next interval (except for the last one)
                if i < intervals - 1:
                    self.logger.debug(
                        'TWAPStrategy',
                        f'Waiting {interval_seconds:.2f} seconds until next interval',
                        {'wait_seconds': interval_seconds}
                    )
                    time.sleep(interval_seconds)
                
            except (APIError, ConnectionError) as e:
                self.logger.error(
                    'TWAPStrategy',
                    f'Error executing interval {interval_num}/{intervals}: {str(e)}',
                    {
                        'interval': interval_num,
                        'error': str(e),
                        'executed_so_far': len(executed_orders)
                    }
                )
                # Continue with remaining intervals despite error
                continue
            
            except Exception as e:
                self.logger.log_error(
                    e,
                    {
                        'component': 'TWAPStrategy',
                        'action': 'execute_interval',
                        'interval': interval_num,
                        'executed_so_far': len(executed_orders)
                    }
                )
                # Continue with remaining intervals despite error
                continue
        
        # Calculate execution summary
        end_time = datetime.now()
        execution_duration = (end_time - start_time).total_seconds()
        
        total_executed_qty = sum(
            float(order.get('executedQty', 0))
            for order in executed_orders
        )
        
        # Calculate average price
        total_value = 0
        for order in executed_orders:
            executed_qty = float(order.get('executedQty', 0))
            avg_price = float(order.get('avgPrice', 0))
            total_value += executed_qty * avg_price
        
        avg_execution_price = total_value / total_executed_qty if total_executed_qty > 0 else 0
        
        # Log final summary
        self.logger.info(
            'TWAPStrategy',
            'TWAP execution completed',
            {
                'symbol': symbol,
                'side': side,
                'total_quantity': total_quantity,
                'total_executed': total_executed_qty,
                'intervals_executed': len(executed_orders),
                'intervals_planned': intervals,
                'avg_price': avg_execution_price,
                'execution_duration_seconds': execution_duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
        )
        
        return executed_orders
