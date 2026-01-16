"""Grid trading strategy implementation."""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.binance_client import BinanceClient, APIError, ConnectionError
from src.logger import BotLogger


class GridStrategy:
    """
    Implements grid trading strategy.
    Places buy and sell limit orders at calculated grid levels within a price range.
    """
    
    def __init__(self, client: BinanceClient, logger: BotLogger):
        """
        Initialize Grid strategy with client and logger.
        
        Args:
            client: BinanceClient instance for order execution.
            logger: BotLogger instance for logging.
        """
        self.client = client
        self.logger = logger
        self.active_orders: Dict[int, Dict[str, Any]] = {}
        self.symbol: Optional[str] = None
        self.is_running = False
    
    def calculate_grid_levels(
        self,
        lower_price: float,
        upper_price: float,
        grids: int
    ) -> List[float]:
        """
        Calculate price levels for grid.
        
        Args:
            lower_price: Lower bound of the price range.
            upper_price: Upper bound of the price range.
            grids: Number of grid levels.
            
        Returns:
            List of price levels for the grid.
            
        Raises:
            ValueError: If parameters are invalid.
        """
        if lower_price <= 0:
            raise ValueError("Lower price must be positive")
        
        if upper_price <= lower_price:
            raise ValueError("Upper price must be greater than lower price")
        
        if grids < 2:
            raise ValueError("Number of grids must be at least 2")
        
        # Calculate price step between grid levels
        price_step = (upper_price - lower_price) / (grids - 1)
        
        # Generate grid levels
        grid_levels = [lower_price + (i * price_step) for i in range(grids)]
        
        self.logger.debug(
            'GridStrategy',
            f'Calculated {grids} grid levels',
            {
                'lower_price': lower_price,
                'upper_price': upper_price,
                'grids': grids,
                'price_step': price_step,
                'grid_levels': grid_levels
            }
        )
        
        return grid_levels
    
    def place_grid_orders(
        self,
        symbol: str,
        grid_levels: List[float],
        quantity_per_grid: float
    ) -> None:
        """
        Place initial grid orders at calculated levels.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            grid_levels: List of price levels for grid orders.
            quantity_per_grid: Quantity to place at each grid level.
            
        Raises:
            APIError: If API returns an error.
            ConnectionError: If connection fails.
        """
        self.logger.info(
            'GridStrategy',
            f'Placing grid orders for {symbol}',
            {
                'symbol': symbol,
                'grid_levels': len(grid_levels),
                'quantity_per_grid': quantity_per_grid
            }
        )
        
        # Get current market price to determine buy/sell placement
        try:
            symbol_info = self.client.get_symbol_info(symbol)
            current_price = float(symbol_info.get('lastPrice', 0))
            
            self.logger.info(
                'GridStrategy',
                f'Current market price: {current_price}',
                {'symbol': symbol, 'current_price': current_price}
            )
        except Exception as e:
            self.logger.error(
                'GridStrategy',
                f'Failed to get current price: {str(e)}',
                {'symbol': symbol, 'error': str(e)}
            )
            raise
        
        # Place orders at each grid level
        for i, price in enumerate(grid_levels):
            try:
                # Determine order side based on price relative to current market
                # Buy orders below current price, sell orders above
                if price < current_price:
                    side = 'BUY'
                elif price > current_price:
                    side = 'SELL'
                else:
                    # Skip if price equals current price
                    self.logger.debug(
                        'GridStrategy',
                        f'Skipping grid level {i+1} at current market price',
                        {'price': price, 'current_price': current_price}
                    )
                    continue
                
                self.logger.info(
                    'GridStrategy',
                    f'Placing {side} order at grid level {i+1}/{len(grid_levels)}',
                    {
                        'level': i+1,
                        'price': price,
                        'side': side,
                        'quantity': quantity_per_grid
                    }
                )
                
                # Place limit order
                order_result = self.client.create_limit_order(
                    symbol=symbol,
                    side=side,
                    quantity=quantity_per_grid,
                    price=price
                )
                
                order_id = order_result.get('orderId')
                self.active_orders[order_id] = {
                    'orderId': order_id,
                    'symbol': symbol,
                    'side': side,
                    'price': price,
                    'quantity': quantity_per_grid,
                    'status': order_result.get('status'),
                    'grid_level': i
                }
                
                self.logger.info(
                    'GridStrategy',
                    f'Grid order placed successfully at level {i+1}',
                    {
                        'order_id': order_id,
                        'level': i+1,
                        'price': price,
                        'side': side,
                        'quantity': quantity_per_grid
                    }
                )
                
            except (APIError, ConnectionError) as e:
                self.logger.error(
                    'GridStrategy',
                    f'Error placing grid order at level {i+1}: {str(e)}',
                    {
                        'level': i+1,
                        'price': price,
                        'error': str(e)
                    }
                )
                # Continue with remaining grid levels
                continue
            
            except Exception as e:
                self.logger.log_error(
                    e,
                    {
                        'component': 'GridStrategy',
                        'action': 'place_grid_order',
                        'level': i+1,
                        'price': price
                    }
                )
                # Continue with remaining grid levels
                continue
        
        self.logger.info(
            'GridStrategy',
            f'Grid initialization complete: {len(self.active_orders)} orders placed',
            {
                'symbol': symbol,
                'total_orders': len(self.active_orders),
                'grid_levels': len(grid_levels)
            }
        )
    
    def monitor_and_rebalance(self) -> None:
        """
        Monitor filled orders and place counter orders.
        This method checks the status of active orders and places new orders
        when grid orders are filled.
        
        Note: This is a simplified implementation. In production, you would
        use websockets or more efficient polling mechanisms.
        """
        if not self.is_running:
            self.logger.warning(
                'GridStrategy',
                'Cannot monitor: strategy is not running',
                {}
            )
            return
        
        self.logger.info(
            'GridStrategy',
            'Starting grid monitoring and rebalancing',
            {
                'symbol': self.symbol,
                'active_orders': len(self.active_orders)
            }
        )
        
        while self.is_running:
            try:
                # Check status of each active order
                orders_to_remove = []
                orders_to_place = []
                
                for order_id, order_info in self.active_orders.items():
                    try:
                        # Query order status
                        order_status = self.client.client.futures_get_order(
                            symbol=order_info['symbol'],
                            orderId=order_id
                        )
                        
                        status = order_status.get('status')
                        
                        # If order is filled, prepare counter order
                        if status == 'FILLED':
                            self.logger.info(
                                'GridStrategy',
                                f'Grid order filled: {order_id}',
                                {
                                    'order_id': order_id,
                                    'side': order_info['side'],
                                    'price': order_info['price'],
                                    'quantity': order_info['quantity']
                                }
                            )
                            
                            # Prepare counter order (opposite side at same price)
                            counter_side = 'SELL' if order_info['side'] == 'BUY' else 'BUY'
                            orders_to_place.append({
                                'symbol': order_info['symbol'],
                                'side': counter_side,
                                'price': order_info['price'],
                                'quantity': order_info['quantity'],
                                'grid_level': order_info['grid_level']
                            })
                            
                            orders_to_remove.append(order_id)
                        
                        # If order is cancelled or expired, remove from tracking
                        elif status in ['CANCELED', 'EXPIRED', 'REJECTED']:
                            self.logger.warning(
                                'GridStrategy',
                                f'Grid order {status.lower()}: {order_id}',
                                {
                                    'order_id': order_id,
                                    'status': status,
                                    'side': order_info['side'],
                                    'price': order_info['price']
                                }
                            )
                            orders_to_remove.append(order_id)
                    
                    except Exception as e:
                        self.logger.error(
                            'GridStrategy',
                            f'Error checking order status: {order_id}',
                            {
                                'order_id': order_id,
                                'error': str(e)
                            }
                        )
                        continue
                
                # Remove filled/cancelled orders from tracking
                for order_id in orders_to_remove:
                    del self.active_orders[order_id]
                
                # Place counter orders
                for order_params in orders_to_place:
                    try:
                        self.logger.info(
                            'GridStrategy',
                            f'Placing counter order: {order_params["side"]} at {order_params["price"]}',
                            order_params
                        )
                        
                        order_result = self.client.create_limit_order(
                            symbol=order_params['symbol'],
                            side=order_params['side'],
                            quantity=order_params['quantity'],
                            price=order_params['price']
                        )
                        
                        new_order_id = order_result.get('orderId')
                        self.active_orders[new_order_id] = {
                            'orderId': new_order_id,
                            'symbol': order_params['symbol'],
                            'side': order_params['side'],
                            'price': order_params['price'],
                            'quantity': order_params['quantity'],
                            'status': order_result.get('status'),
                            'grid_level': order_params['grid_level']
                        }
                        
                        self.logger.info(
                            'GridStrategy',
                            f'Counter order placed successfully: {new_order_id}',
                            {
                                'order_id': new_order_id,
                                'side': order_params['side'],
                                'price': order_params['price']
                            }
                        )
                    
                    except Exception as e:
                        self.logger.error(
                            'GridStrategy',
                            f'Error placing counter order: {str(e)}',
                            {
                                'order_params': order_params,
                                'error': str(e)
                            }
                        )
                        continue
                
                # Sleep before next check (adjust interval as needed)
                if self.is_running:
                    time.sleep(10)  # Check every 10 seconds
            
            except Exception as e:
                self.logger.log_error(
                    e,
                    {
                        'component': 'GridStrategy',
                        'action': 'monitor_and_rebalance'
                    }
                )
                # Continue monitoring despite errors
                if self.is_running:
                    time.sleep(10)
        
        self.logger.info(
            'GridStrategy',
            'Grid monitoring stopped',
            {'symbol': self.symbol}
        )
    
    def stop(self) -> None:
        """
        Cancel all grid orders and stop strategy.
        """
        self.logger.info(
            'GridStrategy',
            'Stopping grid strategy',
            {
                'symbol': self.symbol,
                'active_orders': len(self.active_orders)
            }
        )
        
        self.is_running = False
        
        # Cancel all active orders
        cancelled_count = 0
        failed_count = 0
        
        for order_id, order_info in list(self.active_orders.items()):
            try:
                self.logger.info(
                    'GridStrategy',
                    f'Cancelling order: {order_id}',
                    {
                        'order_id': order_id,
                        'side': order_info['side'],
                        'price': order_info['price']
                    }
                )
                
                # Cancel order via API
                self.client.client.futures_cancel_order(
                    symbol=order_info['symbol'],
                    orderId=order_id
                )
                
                cancelled_count += 1
                
                self.logger.info(
                    'GridStrategy',
                    f'Order cancelled successfully: {order_id}',
                    {'order_id': order_id}
                )
            
            except Exception as e:
                failed_count += 1
                self.logger.error(
                    'GridStrategy',
                    f'Error cancelling order {order_id}: {str(e)}',
                    {
                        'order_id': order_id,
                        'error': str(e)
                    }
                )
                continue
        
        # Clear active orders
        self.active_orders.clear()
        
        self.logger.info(
            'GridStrategy',
            'Grid strategy stopped',
            {
                'symbol': self.symbol,
                'cancelled_orders': cancelled_count,
                'failed_cancellations': failed_count
            }
        )
        
        print(f"\n✓ Grid strategy stopped")
        print(f"   Cancelled orders: {cancelled_count}")
        if failed_count > 0:
            print(f"   Failed cancellations: {failed_count}")
    
    def start(
        self,
        symbol: str,
        lower_price: float,
        upper_price: float,
        grids: int,
        total_investment: float
    ) -> None:
        """
        Initialize and start grid trading.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            lower_price: Lower bound of the price range.
            upper_price: Upper bound of the price range.
            grids: Number of grid levels.
            total_investment: Total investment amount to distribute across grids.
            
        Raises:
            ValueError: If parameters are invalid.
            APIError: If API returns an error.
            ConnectionError: If connection fails.
        """
        # Validate inputs
        if total_investment <= 0:
            raise ValueError("Total investment must be positive")
        
        self.symbol = symbol.upper()
        self.is_running = True
        
        self.logger.info(
            'GridStrategy',
            f'Starting grid strategy for {symbol}',
            {
                'symbol': symbol,
                'lower_price': lower_price,
                'upper_price': upper_price,
                'grids': grids,
                'total_investment': total_investment
            }
        )
        
        # Calculate grid levels
        grid_levels = self.calculate_grid_levels(lower_price, upper_price, grids)
        
        # Calculate quantity per grid based on total investment
        # Simplified: divide total investment by number of grids
        quantity_per_grid = total_investment / grids
        
        self.logger.info(
            'GridStrategy',
            'Grid parameters calculated',
            {
                'grid_levels': len(grid_levels),
                'lower_price': lower_price,
                'upper_price': upper_price,
                'quantity_per_grid': quantity_per_grid
            }
        )
        
        # Place initial grid orders
        self.place_grid_orders(symbol, grid_levels, quantity_per_grid)
        
        self.logger.info(
            'GridStrategy',
            'Grid strategy started successfully',
            {
                'symbol': symbol,
                'active_orders': len(self.active_orders)
            }
        )
